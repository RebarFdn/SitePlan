#schema.py
import datetime
from schematics.models import Model
from schematics.types import StringType, FloatType, IntType, NumberType, DateTimeType, ListType, DictType, ModelType
from schematics.transforms import blacklist

class FormworkSchema(Model):
    unit = StringType()
    plywood = StringType()
    # Formwork for Beams Foundation
    stud = StringType()
    wailer = StringType()
    cleat = StringType()
    ties = StringType()
    # For Slabs
    joist = StringType()
    stringer = StringType()
    shore = StringType
    # For Cantilevers
    kicker = StringType()
    ledger = StringType()
    outrigger = StringType()
    kneebrace = StringType()


    

    stud_spacing = FloatType()
    wailer_spacing = FloatType()

class SlabSchema(Model):
    # Concrete
    roomname = StringType(max_length=50)
    concrete = StringType(max_length=4, min_length=3)
    unit = StringType()
    width = FloatType()
    length = FloatType()
    thickness = FloatType()
    notes = StringType()
    class Options:
        roles = {'public': blacklist('notes')}

class RebarSchema(Model):
    unit = StringType()
    bend = FloatType()
    ## For Concrete slabs
    b1 = StringType()
    b2 = StringType()
    b0 = StringType()
    t0 = StringType()
    t1 = StringType()
    t2 = StringType()
    b1_spacing = FloatType()
    b2_spacing = FloatType()
    b0_spacing = FloatType()
    t0_spacing = FloatType()
    t1_spacing = FloatType()
    t2_spacing = FloatType()
    ## For cmu walls, Stiffeners, Columns
    vb = StringType()
    hb = StringType()
    vb_spacing = FloatType()
    hb_spacing = FloatType()
    vb_height = FloatType()
    hb_length = FloatType()
    ## For Beams, Lintels & Belt courses
    b1_amt = FloatType()
    b2_amt = FloatType()
    t1_amt = FloatType()
    t2_amt = FloatType()
    ## For Beams, Lintels & Belt courses, Stiffeners, Columns
    stirup = StringType()
    stirup_spacing = FloatType()
    taken_at = DateTimeType(default=datetime.datetime.now)
    notes = StringType()
                    
                
    class Options:
        roles = {'public': blacklist('notes')}



class FoundationSchema(Model):
    # Concrete
    tag = StringType(max_length=14)
    grid = StringType(max_length=4)
    concrete = StringType(max_length=4, min_length=3)
    unit = StringType()
    depth = FloatType()
    width = FloatType()
    thickness = FloatType()
    length = FloatType()
    taken_at = DateTimeType(default=datetime.datetime.now)
    notes = StringType()
    class Options:
        roles = {'public': blacklist('notes')}
    

class ColumnSchema(Model):
    # Concrete
    tag = StringType(max_length=14)
    grid = StringType(max_length=4)
    concrete = StringType(max_length=4, min_length=3)
    unit = StringType()
    depth = FloatType()
    width = FloatType()
    height = FloatType()
    amount = IntType()
    taken_at = DateTimeType(default=datetime.datetime.now) 
    notes = StringType()
    class Options:
        roles = {'public': blacklist('notes')}   


class BeamSchema(Model):
    # Concrete
    tag = StringType(max_length=14)
    grid = StringType(max_length=4)
    concrete = StringType(max_length=4, min_length=3)
    unit = StringType()
    depth = FloatType()
    bredth = FloatType()
    length = FloatType()
    taken_at = DateTimeType(default=datetime.datetime.now)
    notes = StringType()
    class Options:
        roles = {'public': blacklist('notes')}


class OpeningSchema(Model):
    tag = StringType(max_length=14)
    unit = StringType()
    thickness = FloatType()
    width = FloatType()
    height = FloatType()
    amount = IntType()
    taken_at = DateTimeType(default=datetime.datetime.now)
    notes = StringType()
    class Options:
        roles = {'public': blacklist('notes')}
    
    
class WallSchema(Model):
    # Concrete
    tag = StringType(max_length=14)
    type = StringType()
    grid = StringType(max_length=4)
    concrete = StringType(max_length=4, min_length=3)
    unit = StringType()
    thickness = FloatType()
    height = FloatType()
    length = FloatType()
    taken_at = DateTimeType(default=datetime.datetime.now)
    notes = StringType()
    columns = ListType(ModelType(ColumnSchema))
    openings = ListType(ModelType(OpeningSchema))
    
    class Options:
        roles = {'public': blacklist('notes')}
