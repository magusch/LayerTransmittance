import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

from app.LayPd import calculation

def datas(material): #load materil's refractive index 
	return(pd.read_csv('app/static/data/%s.csv' %(material), sep=';'))


def interpolate(dts): #interpolate several datas with wvs
	wv_len=[len(dt['wv']) for dt in dts] #len of datas
	wv_index=wv_len.index(max(wv_len)) #take index with the biggest number of points

	wv=dts[wv_index]['wv']

	wv_first=max([dt['wv'].iloc[0] for dt in dts]) #maximum of the first value of wavelenght between all data
	wv_last=min([dt['wv'].iloc[-1] for dt in dts]) #minimum of the last value
	if wv.iloc[-1]>wv_last: #check that wv is less than anothers
		wv=wv[wv<wv_last]
	if wv.iloc[0]<wv_first:
		wv=wv[wv>wv_first]

	wv=np.array(wv)
	n={}
	k={}
	for i,dt in enumerate(dts):
		fn=interp1d(dt['wv'],dt['n'])
		fk=interp1d(dt['wv'],dt['k'])
		n[i+1]=fn(wv)
		k[i+1]=fk(wv)
	# plt.plot(wv,n[1], label='n')
	# plt.plot(wv,k[1], label='k')
	# plt.xlabel('wv,nm')
	# plt.legend()
	# plt.show()
	return wv,n,k


def titles(**parametrs): #make title for the plot
	title={'d':{}, 'n':{}}
	aol=parametrs['amountoflayers']
	d=parametrs['d']
	for index_d,value in d.items():
		#print(index_d,len(value),aol, value)
		if (len(value)==1) & (index_d not in (0, aol)):
			title['d'][(index_d)]=value[0]
		elif value[0]==0:
			next
		else:
			title['d'][index_d]=None

	n_last=parametrs['n'][aol]
	if len(n_last)==1:
		title['n'][aol]=n_last[0]
	else:
		title['n'][aol]=None

	angles=parametrs['angle']
	if len(angles)==1:
		title['angle']=angles[0]
	else:
		title['angle']=None
	try:
		title['material']=parametrs['material']
	except:
		pass
		#title['n'].update(parametrs['n'])
		#title['k']=parametrs['k']
	title['polar']=parametrs['polarization']
	return title


def layer_angle(layer_form_data): #Get data for angle dependency. 
	n, k, d = {}, {}, {}
	for i, layer_data in layer_form_data.items():
		n[i+1]=float(layer_data['n'])
		k[i+1]=float(layer_data['k'])
		d_list=layer_data['d'].split(',')
		d[i+1]=[float(di) for di in d_list]
	return n, k, d


def layer_wv(layer_form_data): #Get data for wv dependency.
	d, material = {}, {}
	for i, layer_data in layer_form_data.items():
		if layer_data['material'] == 'empty':
			continue
		
		material[i+1]=layer_data['material']
		d_list=layer_data['d'].split(',')
		d[i+1]=[float(di) for di in d_list]
	return d, material


def specific_data_angle(angle_data): # range of angle from angle form
	beg, end, step = angle_data['angle_start'], angle_data['angle_finish'], angle_data['angle_step']
	angle = np.arange(beg, end, step)*(2*np.pi)/360

	parametrs = {'angle': angle, 'wv': angle_data['wv']}
	return parametrs




def launch(general_data, layer_form_data, add_data, wit):
	if wit == 'angle': #angle dependecy

		n, k, d = layer_angle(layer_form_data)
		parametrs = specific_data_angle(add_data) #wv and angle
		
	elif wit == 'wv': # wavelenght dependecy
		d, material = layer_wv(layer_form_data)
		dts = [datas(val) for val in material.values()]
		wv, n, k=interpolate(dts)

		angle_list=add_data['angle'].split(',')
		parametrs={'angle':[float(angle)*(2*np.pi)/360 for angle in angle_list], 'wv':wv, 'material':material} #wv and angle

	aol = len(d)+1 #number of layers
	d[aol]=[0]
	k[0], k[aol]=0,0

	parametrs2, n_gen=take_general(general_data, aol) #y_label and polarization
	n.update(n_gen) #n0 and n_last

	parametrs.update(parametrs2) 
	parametrs.update({'n':n, 'k':k, 'd':d, 'amountoflayers':aol, 'wit':wit})
	parametrs['title']=titles(**parametrs) #from parametrs dict make title for plot

	wv,output,path=calculation(parametrs) #run calculation
	return(wv,output,path)	




def take_general(general_data, aol):
	parametrs={'y_label':general_data['y_label'], 'polarization': general_data['polarization']}

	n={}
	#n0_list=general_data['n0'].split(',')
	#n[0]=[float(valy) for valy in n0_list]
	n[0]=float(general_data['n0'])
	nlast_list=general_data['n_last'].split(',')
	n[aol]=[float(valy) for valy in nlast_list]

	return parametrs, n


def divide_data(data):
	general_data, layer_form_data, depend_data = {}, {}, {}
	for key, line in data.items():
		sets = key.split('_')
		field = '_'.join(sets[1:])
		if sets[0] == 'general':
			general_data[field] = line
		elif sets[0] == 'layers':
			split_layer = field.split('-')
			if int(split_layer[1]) in layer_form_data:
				layer_form_data[int(split_layer[1])].update({split_layer[2]: line})
			else:
				layer_form_data[int(split_layer[1])] = {split_layer[2]: line}
		elif sets[0] == 'wv':
			wit = 'wv'
			depend_data[field] = line
		elif sets[0] == 'ang':
			wit = 'angle'
			depend_data[field] = float(line)

	return general_data, layer_form_data, depend_data, wit

