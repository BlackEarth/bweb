
import hashlib, re, sys
from bl import id
from bsql.model import Model

class User(Model):

    relation = 'users'
    pk = ['email']

    MIN_PASSWORD_LEN = 8
    PASSWORD_CHARSET = id.id_chars

    BCRYPT_MODE = '2y'      # because this is used by Apache
    BCRYPT_ROUNDS = 12      # because it takes about .3 seconds
    
    def register(self, cursor=None):
        """try to register the given user, returning any errors that occur."""
        errors = []
        C = self.__class__

        if self.password is None or self.password.strip()=='': 
            self.password = C.random_password()
            autogen = True
        else:
            autogen = False

        errors = C.email_errors(self.email)        
        errors = C.password_errors(self.password)
        
        if errors != []:
            return errors
        else:
            try:
                password = self.pop('password') # temp storage
                self.set_password(password)
                self.insert(cursor=cursor)
                if autogen==True:
                    self.password = password    # put password back if autogenerated (for mailers)
            except:
                if 'IntegrityError' in str(sys.exc_info()[0]):
                    errors += ["That email address is already registered."]                    
                else:
                    errors += [sys.exc_info()[1]]
        return errors

    def authenticate(self, email, password, unverified=False, upgrade=True):
        """Authenticate the login against the database.
        unverified  : whether to authenticate a user for whom the 'verified' field is not True
        upgrade      : whether to upgrade the user's password after successful authentication 
                        using the current preferred encryption method, if out-of-date
        """
        user = self.select_one(where="email ilike %s", vals=[email])   # case-insensitive and secure
        if user is not None and (user.verified or unverified):
            md = re.search("^\$\w+\$", user.pwd)
            if md is None:
                # there is no $...$ at the beginning, 
                # which means it's my old method with SHA256 and separate salt
                if user.pwd == self.encrypt_sha256(password, user.salt):
                    if upgrade==True:
                        user.set_password(password)
                        user.salt = None    # no longer needed.
                        user.commit()                    
                    return user

            else:
                # user.pwd has $...$ at the beginning, which is the "normal" way to do passwords.
                # support various common password encryption schemes
                scheme = md.group()
                verify_pwd = None
                if scheme == '$apr1$':                                          # apache md5
                    from passlib.hash import apr_md5_crypt
                    verify_pwd = apr_md5_crypt.verify
                elif scheme in ['$2y$', '$2a$', '$2b$']:                        # bcrypt 
                    from passlib.hash import bcrypt
                    verify_pwd = bcrypt.verify
                elif scheme == '$1$':                                           # regular md5
                    from passlib.hash import md5_crypt
                    verify_pwd = md5_crypt.verify
                elif scheme == '$6$':                                           # SHA512
                    pass

                if verify_pwd is not None and verify_pwd(password, user.pwd):
                    if upgrade==True and scheme != '$%s$' % self.BCRYPT_MODE:
                        user.set_password(password)
                        user.commit()
                    return user


    # override base class insert() and update() to ensure that email is valid
    def insert(self, **args):
        C = self.__class__
        email_errs = C.email_errors(self.email)
        if email_errs!=[]:
            raise ValueError("Email is not valid: %s. %s" % (self.email, '\n'.join(email_errs)))
        else:
            Model.insert(self, **args)
        
    def insert_or_update(self, **args):
        C = self.__class__
        if C.email_errors(self.email)!=[]:
            raise ValueError("Email is not valid: %s" % self.email)
        Model.insert_or_update(self, **args)

    def before_insert_or_update(self):
        if self.name is not None:
            self.name = re.sub(r'[^\w\s\.\-_]+', r'', self.name, flags=re.U)
        if self.password is not None and self.password.strip() != '':
            self.set_password(self.pop('password'))
    
    def verify(self, id, key):
        """verify the given id & key, returning any errors that occur."""
        user = self.select_one(email=id, salt=key)
        if user is not None:
            user.verify_now()
            return None
        else:
            return "Not verified"

    def verify_now(self):
        C = self.__class__
        self.db.execute("update %s set verified=now() where email=%s" % (C.relation, self.quote(self.email)))
        self = self.reload()

    # -- password stuff -- 

    def set_password(self, password, errors=[]):
        """sets the user's password."""
        C = self.__class__
        pwd_errors = C.password_errors(password)
        if pwd_errors!=[]:
            raise ValueError("password is not valid: %s" % '. '.join(pwd_errors))
        else:
            self.pwd = self.encrypt_password(password)

    @classmethod
    def random_password(C, length=None, charset=None):
        """generate a random password. 
        length defaults to the MIN_PASSWORD_LEN for the class
        charset defaults to the PASSWORD_CHARSET for the class
        """
        length = length or C.MIN_PASSWORD_LEN
        charset = charset or C.PASSWORD_CHARSET
        return id.random_id(length=length, charset=charset)

    @classmethod
    def encrypt_password(C, password, rounds=BCRYPT_ROUNDS, ident=BCRYPT_MODE):
        from passlib.hash import bcrypt
        return bcrypt.encrypt(password, rounds=rounds, ident=ident)

    @classmethod
    def encrypt_sha256(C, password, salt=None):
        """This is my old encrypt_password() function, which I'm keeping around for backward compatibility"""
        import hashlib
        h = hashlib.sha256()
        h.update(password.encode('utf-8'))
        h.update((salt or '').encode('utf-8'))
        return h.hexdigest()

    # -- validations --

    @classmethod
    def email_errors(C, email):
        errors = []
        email_pattern = re.compile(
            r"^[A-Z0-9._%+-]+@(?:[A-Z0-9-]+\.)+[A-Z]{2,}$", flags=re.I + re.U)
        if type(email)!=str: 
            errors.append("Email must be a text string.")
        else:
            email = email.strip()
            if email=='':
                errors.append("Please type your email address.")
            elif re.match(email_pattern, email) is None:
                errors.append("Please type a real email address (you@host.ext).")
        return errors

        
    @classmethod
    def password_errors(C, password):
        # This pattern requires a combination of uppercase, lowercase, and letters.
        # Length must be at least C.MIN_PASSWORD_LEN.
        # Punctuation and non-ASCII letters are optional.
        # password_pattern = re.compile(
        #     "((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{%d,})" % C.MIN_PASSWORD_LEN, flags=re.U)
        errors = []
        if type(password) not in [str, bytes]:
            errors.append("Password must be a string.")
        else:
            pwd = password.strip()
            if len(pwd) < C.MIN_PASSWORD_LEN:
                errors.append("Password must be at least %d characters long." % C.MIN_PASSWORD_LEN)
        return errors

def example_usage_doctest():
    """usage:
    >>> # Connect to the test db
    >>> db=bl.config.db()
    >>> # We need a users table in our test db --
    >>> # the minimal users table is email, pwd, varchar, registered, verified. 
    >>> db.execute("create table users (email varchar primary key, pwd varchar, salt varchar, registered timestamp default now(), verified timestamp)")
    >>> 
    >>> user = User(db, email='nobody@home.now')        # valid in form if not in destination
    >>> user.set_password('insecure')                   # len passowrd >= User.MIN_PASSWORD_LEN
    True
    >>> user.insert()                                   # should be fine, now the user is registered
    >>> user.registered is not None
    True
    >>> 
    >>> # If you try to insert a user with an invalid email address or password, it doesn't work.
    >>> anotheruser = User(db, email='nobody@home')     # not valid
    >>> anotheruser.set_password('short')               # too short -- not set
    False
    >>> anotheruser.insert()
    Traceback (most recent call last):
        ...
    ValueError: email is not valid: nobody@home
    >>> 
    >>> # You can also give the user a random password, but be sure to tell them what it is
    >>> pwd = User.random_password()                    # return this to the user somehow
    >>> user.set_password(pwd)
    True
    >>> user.update()
    >>> 
    >>> # Now we'll try to authenticate our valid first user
    >>> authuser = User(db).authenticate('nobody@home.now', pwd)    # now we use the random pwd
    >>> authuser is not None
    False
    >>> # but it didn't work (no result was returned) because the user isn't verified.
    >>> user.verified == None
    True
    >>> # We could override the need for verification and just let people log in who haven't verified their email address
    >>> authuser = User(db).authenticate('nobody@home.now', pwd, unverified=True)
    >>> authuser is not None
    True
    >>> # But it's best to make users click the emailed link.
    >>> # So let's suppose our user has clicked the "verify" link in the email we sent them
    >>> user.verify_now()                               # method that sets the user's "verified" attribute to now.
    >>> # Now we can authenticate normally
    >>> authuser = User(db).authenticate('nobody@home.now', pwd)
    >>> authuser is not None
    True
    >>> authuser.email == user.email
    True
    >>> 
    >>> # clean up test db
    >>> db.execute("drop table users")
    >>> 
    >>> # So that's how you work with user accounts.
    """    

if __name__ == '__main__':
    import doctest
    doctest.testmod()
