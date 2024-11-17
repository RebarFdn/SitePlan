# SitePlan Platform Utilities 
# Date Nov 26 2022
# Author: Ian Alexander Moncrieffe
import datetime
import json
import typing
from strgen import StringGenerator





def today()->str:
    """Presents the date in a human readable date time string
    Returns:
        str: String of current date and time
    """
    return datetime.date.today().strftime('%B %d, %Y')
    

# Timestamp 
def timestamp(date:str=None)->int:
    """Timestamp returns an integer representation of the current or requested time.
   
    Args:
        date (str, optional): a date string. Defaults to None.

    Returns:
        int: representation of the current time
    Example:
    >>> timestamp()
    1673633512000
    >>> timestamp()
    1673633512000
    """
    if date:
        element = datetime.datetime.strptime(date,"%Y-%m-%d")        
        return int(datetime.datetime.timestamp(element) * 1000)       
    else:
        return  int((datetime.datetime.now().timestamp() * 1000))

def converTime(timestamp:int=None):    
    date = datetime.datetime.fromtimestamp(int(timestamp))
    return date.strftime('%Y-%m-%d %H:%M:%S')

def convert_timestamp(timestamp:int=None):    
    date = datetime.datetime.fromtimestamp(int(timestamp/1000))
    return date.strftime('%Y-%m-%d %H:%M:%S')

def filter_dates(date:str=None, start:str=None, end:str=None):
        day = datetime.datetime.strptime(date, "%Y-%m-%d")
        period_start = datetime.datetime.strptime(start, "%Y-%m-%d")
        period_end = datetime.datetime.strptime(end, "%Y-%m-%d")
        if day.date() >= period_start.date() and day.date() < period_end.date():
            return True
        else:
            return False
    
#----------------------------- ID Generation Service ----------------------------------

class GenerateId:
    '''Generate Unique Human readable Id tags.
    ---
    properties: 
            name: 
                tags
            value: 
                dict
            name: 
                genid
            value: 
                coroutine function
            name: 
                nameid
            value: 
                coroutine function
            name: 
                short_nameid
            value: 
                coroutine function
            name: 
                eventid
            value: 
                coroutine function
            name: 
                short_eventid
            value: 
                coroutine function
            name: 
                gen_id
            value: 
                function
            name: 
                name_id
            value: 
                function
            name: 
                short_name_id
            value: 
                function
            name: 
                event_id
            value: 
                function
            name: 
                short_event_id
            value: 
                function
    '''
    tags = dict(
            doc='[h-z5-9]{8:16}',
            app='[a-z0-9]{16:32}',
            key='[a-z0-9]{32:32}',
            job='[a-j0-7]{8:8}',
            user='[0-9]{4:6}',
            item='[a-n1-9]{8:8}',
            code='[a-x2-8]{24:32}'
        )
        
    async def genid(self, doc_tag:str=None):
        """ 
        Generates a unique id by a required key input.
        :param doc_tag: str
        :return: str
        >>> await genid('user')
        U474390
        >>> await genid('doc')
        ag77vx6n4m

        ---
            Doc Tags: String( doc, app, key, job, user, item, code,task,name)
            UseCase: 
                        >>> import genny
                        >>> from genny import genid
                        >>> from genny import genid as gi
                        
                        >>> id = genny.genid('user')
                        U474390
                        >>> id = genid('user')
                        U77301642
                        >>> id = gi('user')
                        U1593055
                
        """
        
        if doc_tag == 'user':
            #u_id = StringGenerator(str(self.tags[doc_tag])).render(unique=True)
            return f"U{StringGenerator(str(self.tags[doc_tag])).render(unique=True)}"
        return StringGenerator(str(self.tags[doc_tag])).render(unique=True)
            

    async def nameid(self, fn:str='Jane',ln:str='Dear',sec:int=5):
        """
        Name Identification by initials fn='Jane', ln='Dear' and given number sequence sec=5.
        ---    
            UseCase: 
                        >>> import genny
                        >>> from genny import nameid
                        >>> from genny import nameid as nid
                        
                        >>> id = await genny.nameid('Peter','Built',6)
                        PB474390
                        >>> id = await nameid('Peter','Built',5)
                        PB77301
                        >>> id = await nid('Peter','Built',4)
                        PB1593
                        >>> id = await nid() # default false id 
                        JD1951                        
                
        """
        code = '[0-9]{4:%s}'% int(sec)
        return f"{fn[0].capitalize()}{ln[0].capitalize()}{StringGenerator(str(code)).render(unique=True)}"
               

    async def short_nameid(self, fn:str='Jane',ln:str='Dear',sec:int=2):
        """
        Name Identification by initials fn='Jane', ln='Dear' and given number sequence sec=5.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import short_nameid
                        >>> from genny import short_nameid as id
                        
                        >>> id = genny.short_nameid('Peter','Built',2)
                        >>> id = short_nameid('Peter','Built')
                        >>> id = id(p','b',3)
                        >>> id = id() # default false id 
                        
                Yeilds ... PB47
                        ... PB54
                        ... PB69
                        ... JD19
        
        """
        code = '[0-9]{2:%s}'% int(sec)
        return f"{fn[0].capitalize()}{ln[0].capitalize()}{StringGenerator(str(code)).render(unique=True)}"
        

    async def eventid(self, event,event_code,sec=8):
        """EventId 
            Event Identification by initials fn='Jane', ln='Dear' and given number sequence sec=5.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import eventid
                        >>> from genny import eventid as id
                        
                        >>> id = genny.eventid('Product','LAUNCH',6)
                        >>> id = eventid('Product','LAUNCH',5)
                        >>> id = id('Product', 'LAUNCH',4)                       
                Yeilds ... PROLAUNCH-884730
                        ... PROLAUNCH-18973
                        ... PROLAUNCH-4631                       
        
        """
        code = '[0-9]{4:%s}'% int(sec)
        return f"{event[:3].upper()}{event_code}-{StringGenerator(str(code)).render(unique=True)}"
        

    async def short_eventid(self, event,event_code,sec=2):
        """ShortEventId 
            Event Identification by initials fn='Jane', ln='Dear' and given number sequence sec=2.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import shorteventid
                        >>> from genny import shorteventid as id
                        
                        >>> id = genny.shorteventid('Product','LAUNCH',2)
                        >>> id = shorteventid('Product','LAUNCH')
                        >>> id = id('Product', 'LAUNCH',3)
                Yeilds ... PROLAUNCH-88
                        ... PROLAUNCH-90
                        ... PROLAUNCH-461                       
        
        """
        code = '[0-9]{2:%s}'% int(sec)
        return f"{event[:3].upper()}{event_code}-{StringGenerator(str(code)).render(unique=True)}"
        
        
    def gen_id(self, doc_tag:str=None):
        """ 
            Doc Tags: String( doc, app, key, job, user, item, code,task,name)
            UseCase: 
                        >>> import genny
                        >>> from genny import genid
                        >>> from genny import genid as gi
                        
                        >>> id = genny.genid('user')
                        >>> id = genid('user')
                        >>> id = gi('user')
                Yeilds ... U474390
                        ... U77301642
                        ... U1593055
        
        """
        
        if doc_tag == 'user':
            #u_id = StringGenerator(str(self.tags[doc_tag])).render(unique=True)
            return f"U{StringGenerator(str(self.tags[doc_tag])).render(unique=True)}"
        return StringGenerator(str(self.tags[doc_tag])).render(unique=True)
            

    def name_id(self, fn:str='Jane',ln:str='Dear',sec:int=5):
        """ 
            Name Identification by initials fn='Jane', ln='Dear' and given number sequence sec=5.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import nameid
                        >>> from genny import nameid as nid
                        
                        >>> id = genny.nameid('Peter','Built',6)
                        >>> id = nameid('Peter','Built',5)
                        >>> id = nid('Peter','Built',4)
                        >>> id = nid() # default false id 
                        
                Yeilds ... PB474390
                        ... PB77301
                        ... PB1593
                        ... JD1951
        
        """
        code = '[0-9]{4:%s}'% int(sec)
        return f"{fn[0].capitalize()}{ln[0].capitalize()}{StringGenerator(str(code)).render(unique=True)}"
               

    def short_name_id(self, fn:str='Jane',ln:str='Dear',sec:int=2):
        """ 
            Name Identification by initials fn='Jane', ln='Dear' and given number sequence sec=5.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import short_nameid
                        >>> from genny import short_nameid as id
                        
                        >>> id = genny.short_nameid('Peter','Built',2)
                        >>> id = short_nameid('Peter','Built')
                        >>> id = id(p','b',3)
                        >>> id = id() # default false id 
                        
                Yeilds ... PB47
                        ... PB54
                        ... PB69
                        ... JD19
        
        """
        code = '[0-9]{2:%s}'% int(sec)
        return f"{fn[0].capitalize()}{ln[0].capitalize()}{StringGenerator(str(code)).render(unique=True)}"
        

    def event_id(self, event,event_code,sec=8):
        """EventId 
            Event Identification by initials fn='Jane', ln='Dear' and given number sequence sec=5.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import eventid
                        >>> from genny import eventid as id
                        
                        >>> id = genny.eventid('Product','LAUNCH',6)
                        >>> id = eventid('Product','LAUNCH',5)
                        >>> id = id('Product', 'LAUNCH',4)                       
                Yeilds ... PROLAUNCH-884730
                        ... PROLAUNCH-18973
                        ... PROLAUNCH-4631                       
        
        """
        code = '[0-9]{4:%s}'% int(sec)
        return f"{event[:3].upper()}{event_code}-{StringGenerator(str(code)).render(unique=True)}"
        

    def short_event_id(self, event,event_code,sec=2):
        """ShortEventId 
            Event Identification by initials fn='Jane', ln='Dear' and given number sequence sec=2.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import shorteventid
                        >>> from genny import shorteventid as id
                        
                        >>> id = genny.shorteventid('Product','LAUNCH',2)
                        >>> id = shorteventid('Product','LAUNCH')
                        >>> id = id('Product', 'LAUNCH',3)
                Yeilds ... PROLAUNCH-88
                        ... PROLAUNCH-90
                        ... PROLAUNCH-461                       
        
        """
        code = '[0-9]{2:%s}'% int(sec)
        return f"{event[:3].upper()}{event_code}-{StringGenerator(str(code)).render(unique=True)}"
        

class Security:
    def safe_file_storage(self, item:str, item_1:str):
        import werkzeug
        from werkzeug.datastructures import FileStorage        
        try:
            file = FileStorage(
                stream=None, 
                filename=None, 
                name=None, 
                content_type=None, 
                content_length=None, 
                headers=None
                )
            return dir(werkzeug.datastructures) #safe_str_cmp(item, item_1)
        except Exception as ex:
            return str(ex)
        finally: print()# del(safe_str_cmp)


# Currency dollars
def to_dollars(amount:float=None):
    if amount:
        amount = float(amount)
        if amount >= 0:
            return '${:,.2f}'.format(amount)
        else:
            return '-${:,.2f}'.format(-amount)
    else:
        return 0
    

       
def generate_id(name:str=None)->str:
        ''' Generates a unique Human readable id, also updates the worker data'''              
        gen = GenerateId()
        fln = name.split(' ') # first, last name
        try:           
            return gen.name_id(fn=fln[0], ln=fln[1]) 
        except:
            return gen.name_id('C', 'W')
        finally:           
            del(gen)
            del(fln)


def generate_docid()->str:
    """Generates a unique document id

    Returns:
        str: Unique string of letters and numbers 
    """           
    gen:GenerateId = GenerateId()       
    try: return gen.gen_id(doc_tag='item')        
    finally: del(gen)
            
 
def hash_data(data:dict=None)->str:
    """_summary_

    Args:
        data (dict, optional): _description_. Defaults to None.

    Returns:
        str: _description_
    """
    import hashlib    
    try:            
        return hashlib.md5(json.dumps(data).encode()).hexdigest()
    except Exception as e:
        return str(e)
    finally:
        del(hashlib)
        
    
def validate_hash_data( hash_key:bytes=None, data:dict=None):
        import hashlib        
        try:
            hash_obj = hashlib.md5(json.dumps(data).encode()).hexdigest()           
            return hash_key == hash_obj
        except Exception as e:
            return str(e)
        finally:
            del(hashlib)
            

# Metadata Process 
def load_metadata(property:str=None, value:typing.Any=None, db:dict={}):
    meta_data:dict = {
        "created": 0, 
        "database": {"name":db.get('local'), "partitioned":db.get('local_partitioned')},              
    }    
    if property and value:
        meta_data[property] = value
        return meta_data

    elif not property and value:
        return meta_data
    
    elif property and not value:
        return { property: meta_data.get(property)}
    return meta_data


def set_metadata(property:str=None, value:typing.Any=None, metadata:dict={}):
    if property and value:
        metadata[property] = value
        return metadata
    elif not property and value:
        return metadata
    
    elif property and not value:
        return metadata.get(property)
    return metadata
    

def exception_message(message:str=None):
    return f"""<div class="uk-alert-warning" uk-alert>
        <a href class="uk-alert-close" uk-close></a>
        <p>{ message }</p>
    </div>"""



# test
def test_secure_safe_compare(s1, s2):
    s = Security()
    print(s.safe_file_storage(s1, s2))

#test_secure_safe_compare('buff', 'buff')

def test_delete():
    '''Theory that deletions should be done in an order 
        that safely unlock resources 
    '''
    r = 1       # stand alone has 0 dependent
    r2 = r * 2  # has 1 dependent
    r3 = r + r2 # has 2 dependents
    r4 = r + r3 # has 3 dependent
    rs = dict( 
        r = r, 
        r2 = r2,
        r3 = r3,
        r4 = r4, 

    )
    try: print(rs) 
    except: print(r)
    finally: 
        print("Done")
        del(r3)
        del(r) 
        del(r4) 
        del(r2) 
        del(rs)

if __name__ == "__main__":
    print('Testing from SitePlan utils')
    data = {'na': "pete", 'aa': 5 }
    hd = hash_data(data=data)
    print(hd)
    
    vdt = validate_hash_data( hash_key=hd, data=data)
    print(vdt)

