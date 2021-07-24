import os, json
from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.utils import secure_filename

from forms import GeneralForm, AngleForm, LayerForm, WavelengthForm

from app.t8data import launch, divide_data, datas
from app.LayPd import find_d_met

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder='app/static/')

app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'app/static/plot'),
    static_folder='app/static/',
    WTF_CSRF_ENABLED= False )


def layers(n=3):
    layer_form = []
    for i in range(n):
        layer_form.append(LayerForm(prefix="layers_form-%s" %(i)))
    return layer_form


@app.route('/<int:number_layers>', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def wavelength(number_layers=4):
    form = GeneralForm(prefix="general_")
    layers_forms = layers(number_layers)
    wv_form = WavelengthForm(prefix="wv_")

    return render_template('wv_index.html', form=form, layer_form=layers_forms, wv_form=wv_form,
                           title='Wavelength dependence')


@app.route('/angle/<int:number_layers>', methods=['GET', 'POST'])
@app.route('/angle', methods=['GET', 'POST'])
def angle(number_layers=4):
    form = GeneralForm(prefix="general_")
    layers_forms = layers(number_layers)
    angle_form = AngleForm(prefix="ang_")
        
    return render_template('angle.html', form=form, layer_form=layers_forms, angle_form=angle_form,
                           title='Angle dependence')


@app.route('/plasmon', methods=['GET', 'POST'])
def plasmon():
    return render_template('plasmon.html', title='Plasmon')

@app.route('/plotting', methods=['POST'])
def plotting():
    data = request.form.to_dict()
    general_data, layer_form_data, depend_data, wit = divide_data(data)
    mat, output_csv, image_path = launch(general_data, layer_form_data, depend_data, wit=wit)
    image_path = url_for('static', filename='plot/' + image_path)
    return render_template('answer.html', output_csv=output_csv, mat=mat, IMAGE=image_path, title = 'The Graph')


@app.route('/imag_real', methods=['POST'])
def imag_real():
    return render_template('imag_real.html')


@app.route('/ajax_imag_real')
def ajax_imag_real():
    query = request.args.get('query').upper()
    return json.dumps('ANSWER!!!!')

@app.route('/refraction_for_material/<string:material>')
def ajax_refractive_for_material(material):
    wv = request.args.get('wv')
    if wv==None:
        return 'None. Need to type wavelength'
    df = datas(material)

    if df is not None:
        df['wv_mean'] = abs(df['wv']-float(wv))
        index = df.where(df['wv_mean']==min(df['wv_mean'])).first_valid_index()
        answer = {'wv': float(df['wv'][index]), 'n': float(df['n'][index]), 'k': float(df['k'][index])}
        return json.dumps(answer)
    else:
        return 'None material'


@app.route('/get_plasmon')
def get_plasmon():
    parameters = {
        'wv' : request.args.get('wv'),
        'n0' : request.args.get('n0'),
        'n1': request.args.get('n1'), 'k1': request.args.get('k1'),
        'n2': request.args.get('n2')
    }
    d_met, theta_min = find_d_met(parameters)
    response = {'d_met': round(d_met,3), 'theta':round(theta_min,3)}
    return json.dumps(response)


if __name__ == '__main__':
    app.run(debug=True)