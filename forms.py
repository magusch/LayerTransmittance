from flask_wtf import FlaskForm
from wtforms import StringField,FloatField,SelectField,RadioField, SubmitField, FieldList,FormField
#from wtforms.validators import DataRequired

class General_form(FlaskForm):
    #zero-layer
    n0 = StringField('n0',default=1.5)

    #last layer
    n_last=StringField('n for last layer', default=1)
    #wv=StringField('Wavelength, nm')
    polarization=RadioField("What's polarization", choices=[('S','s-polarization'),('P','p-polarization')], default='S')
    y_label=RadioField('Reflection or Transmintence', choices=[('R','Reflection'),('T','Transmittance')], default='R')

    
class Layer_Form(FlaskForm):
    d = StringField('d, nm', default='50')
    material=SelectField('What is material', choices=[('empty','Empty'),('Ag', 'Ag'),('Zn', 'Zn'),('Chr', 'Chr'), ('Al','Al'), ('Au','Au'), ('ZnO','ZnO')], default='Zn')
    n=FloatField('n', default=1)
    k=FloatField('k', default=0)


class wavelength_form(FlaskForm):
	angle = StringField('Angle, degrees', default=0) #several

class Angle_form(FlaskForm):
	wv = FloatField('Wavelength, nm', default=360)

	angle_start = FloatField('Angle (first value)', default=0)
	angle_finish = FloatField('Angle (last value)', default=90)
	angle_step = FloatField('Angle step', default=1)