import os
from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.utils import secure_filename

from forms import General_form, Angle_form,Layer_Form,wavelength_form

from app.t8data import launch

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder='app/static/')

app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'app/static/plot'),
    static_folder='app/static/',
    WTF_CSRF_ENABLED= False )
#app.config['WTF_CSRF_ENABLED'] = False

def layers(n=3):
    layer_form=[]
    for i in range(n):
        layer_form.append(Layer_Form(prefix="form%s" %(i)))
    return layer_form


@app.route('/<int:number_layers>', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def wavelenght(number_layers=4):
    form = General_form()
    layers_forms=layers(number_layers)
    wv_form=wavelength_form()
    if form.validate_on_submit():
        general_data=form.data
        wv_data=wv_form.data
        layer_form_data={}
        for i in range(len(layers_forms)):
            layer_form_data[i]=layers_forms[i].data

        #q=form.data
        #z=layers_forms.data
        #ans, mat, image_path=takedata(q,z)
        wv, output_csv,  image_path=launch(general_data, layer_form_data, wv_data, wit='wv')
        image_path=url_for('static', filename='plot/'+image_path)
        #output_csv=url_for('static', filename='plot/'+output_csv)
        #image_path='app/'+image_path
        return render_template('answer.html', output_csv=output_csv, mat=wv, IMAGE=image_path)
        #return render_template('answer.html', general=general_data, layers=layer_form_data, additional=wv_data )

    return render_template('wv_index.html', form=form, layer_form=layers_forms, wv_form=wv_form)
    #return render_template( form=form, forms=layers_forms)
    #return 'Hello, World!'


# @app.route('/plot', methods=['GET', 'POST'])
# def plot(q):
#     if form.validate_on_submit():
#         # mat=form.material.data
#         # angle=form.angle.data
#         # n0=form.n0.data
#         # d=form.d.data
#         # q=form.data
#         print('hi')
#     return render_template('answer.html', q=q)

@app.route('/angle/<int:number_layers>', methods=['GET', 'POST'])
@app.route('/angle', methods=['GET', 'POST'])
def angle(number_layers=4):
    #form_wv = General_form()
    form = General_form()
    layers_forms=layers(number_layers)
    angle_form=Angle_form()

    #layers_forms=Layer_Form()
    #form = Angle_depends_form()
    if layers_forms[0].validate_on_submit():
        #wv_data={'wv':form_wv.wv.data}
        general_data=form.data
        angle_data=angle_form.data
        layer_form_data={}
        for i in range(len(layers_forms)):
            layer_form_data[i]=layers_forms[i].data
        mat,output_csv,image_path=launch(general_data, layer_form_data, angle_data, wit='angle')
        image_path=url_for('static', filename='plot/'+image_path)
        return render_template('answer.html', output_csv=output_csv, mat=mat, IMAGE=image_path)
        #return render_template('answer.html', general=general_data, layers=layer_form_data, additional=angle_data )
        #flash('Material: {}, d={}'.format(
        #    mat, d))
        
    return render_template('angle.html', form=form, layer_form=layers_forms,angle_form=angle_form)









if __name__ == '__main__':
    app.run(debug=True)