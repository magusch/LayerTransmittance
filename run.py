import os, json
from flask import Flask, render_template, request, url_for, redirect, flash

from forms import GeneralForm, AngleForm, LayerForm, WavelengthForm, AddMaterialForm

from app.searching_plasmon import SearchingPlasmonPlace
from app.prepare_data import PrepareData
from app.saving_plot import TransmittancePlotter

from utils.materials_ri import available_materials as am, download_file, prepare_material_file, divide_url_ri

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder='/layer_transmittance/app/static/')

app.config.update(
    UPLOADED_PATH='/layer_transmittance/app/uploads/', #os.path.join(basedir, 'app/static/plot'),
    WTF_CSRF_ENABLED= False )


def layers(n=3):
    layer_form = []
    choices = list(map(lambda x: (x, x), am()))
    for i in range(n):
        layer_form.append(LayerForm(prefix="layers_form-%s" %(i)))
        layer_form[-1].material.choices = choices
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
                           title='Angle dependence', materials = am())


@app.route('/plasmon', methods=['GET', 'POST'])
def plasmon():
    return render_template('plasmon.html', title='Plasmon')


@app.route('/imag_real', methods=['POST'])
def imag_real():
    return render_template('imag_real.html')


@app.route('/refraction_for_material/<string:material>')
def ajax_refractive_for_material(material):
    wv = request.args.get('wv')
    if wv == None:
        return json.dumps({'error':"None. Need to type wavelength. Example: 'refraction_for_material/ag/?wv=403'"})
    answer = PrepareData().refractive_index_for_wavelength(material, wv)
    if answer is not None:
        return json.dumps(answer)
    else:
        return json.dumps({'error':'None material.'})


@app.route('/add_material/', methods=['GET', 'POST']) #<string:materials>
def add_material():
    if request.method == 'POST':
        url = request.form['url_ri']
        if '.csv' not in url:
            ri_url_dict = divide_url_ri(url)
            url = f"https://refractiveindex.info/tmp/database/data-nk/{ri_url_dict['shelf']}/{ri_url_dict['book']}/{ri_url_dict['page']}.csv"
            material = ri_url_dict['book']
        else:
            material = url.split('/')[-2]
        download_file(url, material)
        prepare_material_file()

    form = AddMaterialForm()
    return render_template('add_material.html', title='Add Material', form=form)


@app.route('/get_plasmon')
def get_plasmon():
    parameters = {
        'wv' : request.args.get('wv'),
        'n0' : request.args.get('n0'),
        'n1': request.args.get('n1'), 'k1': request.args.get('k1'),
        'n2': request.args.get('n2')
    }
    plasmon_class = SearchingPlasmonPlace(parameters)
    d_met, theta_min = plasmon_class.find_d_met()
    response = {'d_met': round(d_met,3), 'theta':round(theta_min,3)}
    return json.dumps(response)


@app.route('/plotting', methods=['GET', 'POST'])
def plotting():
    data = request.form.to_dict()

    # Prepare data from the form
    prepare_data_class = PrepareData()
    general_data, layer_form_data, depend_data, wit = prepare_data_class.divide_data(data)
    parameters = prepare_data_class.get_parameters(general_data, layer_form_data, depend_data, wit=wit)

    # Calculate and plot using the parameters from the form
    plotter = TransmittancePlotter(**parameters)
    fig, output_csv = plotter.run()

    # Transform the constructed graph into html
    plot_html = fig.to_html(full_html=False)

    return render_template("plotly_index.html", plot=plot_html, output_csv=output_csv, title = 'The Graph New')


if __name__ == '__main__':
    app.run(debug=True)