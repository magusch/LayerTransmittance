from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, RadioField


class GeneralForm(FlaskForm):
    #zero-layer
    n0 = StringField('n0',default = 1.5)

    #last layer
    n_last = StringField('n for last layer', default = 1.0)

    polarization = RadioField("What's polarization", choices=[('S','s-polarization'),('P','p-polarization')], default = 'P')
    y_label = RadioField('Reflection or Transmintence',
                       choices=[('R','Reflection'),('T','Transmittance'),('OD','Optical density')], default = 'R')

    
class LayerForm(FlaskForm):
    d = StringField('d, nm', default = '0')
    material = SelectField('What is material',
                         choices = [('empty','Empty'),('Ag', 'Ag'),('Zn', 'Zn'),('Chr', 'Chr'), ('Al','Al'), ('Au','Au'),
                                  ('ZnO','ZnO'), ('MgF2','MgF2'), ('SiO','SiO'), ('Au_44nm', 'Au_44nm')], default = 'Zn')
    n = FloatField('n', default = 1)
    k = FloatField('k', default = 0)


class WavelengthForm(FlaskForm):
    angle = StringField('Angle, degrees', default=0) #several

class AngleForm(FlaskForm):
    wv = FloatField('Wavelength, nm', default = 360)
    angle_start = FloatField('Angle (first value)', default = 0)
    angle_finish = FloatField('Angle (last value)', default = 90)
    angle_step = FloatField('Angle step', default = 0.1)

class PlasmonForm(FlaskForm):
    wv = FloatField('Длина волны, нм', default=403.3)
    n0 = FloatField('n0', default=1.512)
    n1 = FloatField('n1', default=1.3)
    k1 = FloatField('k1', default=0)
    n2 = FloatField('n_env', default=1.0)