import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import time
#from io import BytesIO

pi = np.pi
j = 1j
ylab = {'R':'Коэффициент отражения', 'T':'Коэффициент пропускания', 'OD':'Оптическая плотность'}
output_url = {}

import matplotlib
matplotlib.use('agg')


def layer_transmittance(parametrs,d,teta):
    wv = parametrs['wv']
    n,k = parametrs['n'],parametrs['k']
    amountoflayers = parametrs['amountoflayers']
    #print(parametrs)
    r,t,be = {},{},{}


    M = np.array([[1,0],[0,1]])

    keys = list(n.keys())
    keys.sort()
    io = 0 #zero layer

    matr_delta = {io:np.array([[1,0],[0,1]])}
    eps = {io:n[io]**2}

    kx = np.sqrt(eps[io])*np.sin(teta)
    kz = {io:np.array((2*pi/wv)*np.sqrt(eps[io]-kx**2))}

    for i in keys[1:]:
        try:
            eps[i] = np.array((n[i]+j*k[i])**2, dtype = np.complex)
        except Exception as e:
            print(e)
            eps[i] = np.array((n[i])**2, dtype = np.complex)

        kz[i] = ((2*pi/wv)*np.sqrt(eps[i]-kx**2))

        try:
            be[i] = kz[i]*d[i]
        except:
            be[i] = np.inf

        #______________
        if parametrs['polarization']=='S': # S-polarization
            t[i] = 2*kz[io]/(kz[io]+kz[i]) #S-поляризация
            r[i] = (kz[io]-kz[i])/(kz[io]+kz[i])
        else: 							  # P-polarization
            t[i] = 2*kz[io]*np.sqrt(eps[io]*eps[i])/(eps[i]*kz[io]+eps[io]*kz[i])
            r[i] = (eps[i]*kz[io]-eps[io]*kz[i])/(eps[i]*kz[io]+eps[io]*kz[i])

        matr = np.array([[np.array(1/t[i]), np.array(r[i]/t[i])],[np.array(r[i]/t[i]), 0]])
        matr[1][1] = 1/t[i]	#to make matrix 2x2 with another matrix
        M = np.dot(M,np.dot(matr_delta[io],matr))

        matr_delta[i] = np.array([[np.exp(-j*be[i]), 0],[0, np.exp(j*be[i])]])
        io = i #save index of this layer for next calculation (it is because we use dict with deleting empty layer)


    M = M.dot(np.array([[1],[0]]))


    Reflection = abs(M[1][0]/M[0][0])**2

    Transmission = (1/M[0][0])
    Trans = np.real((kz[amountoflayers]/kz[0])*abs(Transmission)**2)
    if np.min(Trans) != 0: #TODO: исправить если Trans = 0 в одном месте
        OD  =  np.log10(1/Trans)
    else:
        OD = Trans*0
    output = {'R': Reflection, 'T': Trans, 'OD': OD}


    return output, wv


def imag_real(parametrs, d_met):
    wv = float(parametrs['wv'])
    n = [parametrs['n0'], parametrs['n1'], parametrs['n2']]
    n = [float(i) for i in n]
    k = float(parametrs['k1'])
    k2 = float(0.00085466)
    theta = parametrs['theta']


    eps_g = n[0]**2
    eps_met = np.array((n[1] + j * k) ** 2, dtype=np.complex)
    eps_de1 = np.array((n[2]+j*k2)**2, dtype=np.complex)

    #n_met = np.array((n[1] + j * k), dtype=np.complex)
    sin = np.array(np.sin(theta), dtype=np.complex)
    kx = np.sqrt(eps_g)*sin
    kz=[np.array((2*pi/wv)*np.sqrt(eps_g-kx**2))]
    kz.append((2 * pi / wv) * np.sqrt(eps_met - kx ** 2))
    kz.append((2 * pi / wv) * np.sqrt(eps_de1 - kx ** 2))


    r = []
    r.append((eps_met * kz[0] - eps_g * kz[1]) / (eps_met * kz[0] + eps_g * kz[1]))
    r.append((eps_de1 * kz[1] - eps_met * kz[2]) / (eps_de1 * kz[1] + eps_met * kz[2]))
    #r[i] = (eps[i] * kz[io] - eps[io] * kz[i]) / (eps[i] * kz[io] + eps[io] * kz[i])

    sin_theta = np.sqrt((eps_met*eps_de1)/(eps_met+eps_de1)).real/n[0]

    d_min = 0
    theta_min = 0

    #min_z = 0.02
    min_z = abs(d_met[1]-d_met[0])/2

    for d in d_met:
        r012_chisl = r[0] + r[1] * np.exp(j * 2 * kz[1] * d)
        x = r012_chisl.real
        y = r012_chisl.imag

        zero_array = np.sqrt(x**2+y**2)
        min_z_index = list(zero_array).index(zero_array.min())
        if zero_array[min_z_index]<min_z:
            min_z = zero_array[min_z_index]
            d_min = d
            theta_min = parametrs['theta'][min_z_index]

        # x_zero = np.where(abs(x)-min_z/2 < 0)
        # y_zero = np.where(abs(y)-min_z/2 < 0)
        # zero = [zero for zero in x_zero[0] if zero in y_zero[0]]
        # o = 0
        # for z in zero:
        #     if abs((abs(x[z])-min_z/2)+(abs(y[z])-min_z/2))>1.5*min_z: continue
        #     min_z = abs((abs(x[z])-min_z/2)+(abs(y[z])-min_z/2))
        #     print(f"min_z: {min_z}")
        #     #print(parametrs['theta'][z])
        #     d_min=d
        #     theta_min = parametrs['theta'][z]
        #     if o == 0: plt.text(x[z]+0.03*(max(x)), y[z]+0.1*(max(y)), f"{round(d,1)} нм – {round(parametrs['theta'][z] / (2 * 3.1415 / 360), 2)}°")
        #     o=1
        #plt.plot(x, y, label=f'{round(d,2)}')
        # if np.where(y == 0)[0]:
        #     print("!!!!!")
        #     print(np.where(x == 0)[0])

    #plt.plot(x, y, label=f'{d}')
    # line_x = np.arange(-0.1*(max(x)-min(x)), 0.1*(max(x)-min(x)), 0.03)
    # line_zero_x = 0 * np.arange(len(line_x))
    # line_y = np.arange(-0.1 * (max(y) - min(y)), 0.1 * (max(y) - min(y)), 0.03)
    # line_zero_y = 0 * np.arange(len(line_y))
    # plt.plot(line_zero_x, line_x, 'k-.')
    # plt.plot(line_y, line_zero_y, 'k-.')
    # plt.title(f"n_Аналит: {n[-1]}")
    # plt.text(x[0], y[0], f"{round(parametrs['theta'][0]/(2*3.1415/360),2)}°")
    # plt.text(x[-1], y[-1], f"{round(parametrs['theta'][-1]/(2*3.1415/360),2)}°")

    # plt.xlabel('real')
    # plt.ylabel('imag')
    # plt.legend()
    # plt.show()

    return d_min, theta_min


# parametrs = {'wv': 403.3,
# 	'n': [1.512, #Призма
# 			1.5404,    # Метал
# 			1.33], # Аналит
# 	'k': 1.9249, #Метал
# }
def find_d_met(parameters):
    parameters['theta'] = np.arange(0, 1.57, 0.00001)

    d_range_dict = {'d_range_min': 5, 'd_range_max': 100, 'd_range_step': 5}

    while d_range_dict['d_range_step'] > 0.001:
        d_range = np.arange(d_range_dict['d_range_min'], d_range_dict['d_range_max'], d_range_dict['d_range_step'])
        d_met_new, theta_min_new = imag_real(parameters, d_range)

        if d_met_new == 0: break
        d_met, theta_min = d_met_new, theta_min_new

        if d_met != 0:
            d_met_i = list(d_range).index(d_met)
        else:
            break

        if d_met_i != 0:
            d_range_dict['d_range_min'] = d_range[d_met_i - 1]
        else:
            d_range_dict['d_range_min'] = d_range[d_met_i] - d_range_dict['d_range_step'] / 10

        if d_met_i != list(d_range).index(d_range[-1]):
            d_range_dict['d_range_max'] = d_range[d_met_i + 1]
        else:
            d_range_dict['d_range_max'] = d_range[d_met_i] + d_range_dict['d_range_step'] / 10

        d_range_dict['d_range_step'] = (d_range_dict['d_range_max'] - d_range_dict['d_range_min']) / 10

    return (d_met, theta_min)

# import numpy as np
#
# parametrs = {'wv': 632.8,
# 	'n': [1.512, #Призма
# 			0.18508,    # Метал
# 			1.0], # Аналит
# 	'k': 3.4233, #Метал
# 	'theta': np.arange(0,1.5, 0.0001)
# }
# d_met = range(35,50,5)
#
# from app.LayPd import imag_real
#
# x,y=imag_real(parametrs, d_met)


def het(d, parametrs, height = {}, o = 1):  #height - dict for calculation; d – dict with all values of height layers, o – what layer
    #het(d = {1:[40,20,0], 2:[30,0], 3:[50,100]}, height = {0:0},  layer = 1)
    for h in d[o]:
        height[o] = float(h)
        if (h==0) & (o != parametrs['amountoflayers']):
            height.pop(o)
            parametrs['n'].pop(o)
            parametrs['k'].pop(o)
        try:
            wv,output = het(d,parametrs, height, o+1)
        except:
            if parametrs['wit']=='angle':
                wv,output = calc_on_teta(height, **parametrs)
            else:
                wv,output = calc_on_wv(height, **parametrs)
    return(wv,output)



def calc_on_wv(height, **parametrs): #dependecy of wv with loop for list of angle
    angle = parametrs['angle']
    title = parametrs['title']
    for teta in angle:
        output, wv = layer_transmittance(parametrs,height,teta)
        labl = labels_good(title,parametrs, height, teta)

        # save_file = np.vstack([['wv', 'R', 'T'], np.array([wv,output['R'],output['T']]).transpose()])

        # filename = str(time.time()) +'.csv'
        # csv_path = 'app/static/plot/'+filename

        # np.savetxt(csv_path, save_file, delimiter = ";",fmt = '%s')

        plt.plot(wv,output[parametrs['y_label']], label = labl)
        plt.xlabel('Длина Волны, нм')

        output_url.update(output_urls(parametrs, wv, output, labl))

    return(wv,output_url)


def calc_on_teta(height, **parametrs): #dependecy of angle
    angle = parametrs['angle']
    title = parametrs['title']
    labl = labels_good(title, parametrs, height, angle)

    output, wv = layer_transmittance(parametrs,height,angle)
    angle_inDegree = angle*360/(2*pi)

    plt.plot(angle_inDegree, output[parametrs['y_label']], label=labl) #(angle*360/(2*pi))

    plt.xlabel('Угол, градусы')

    #find_width(angle_inDegree, output[parametrs['y_label']], height[2])

    output_url.update(output_urls(parametrs, angle_inDegree, output,labl))

    return wv, output_url

def find_width(x,y, d):
    height = max(y) - min(y)

    y_half = np.where(abs(y-height/2) < height*0.0001)
    if y_half[0] is False: return
    #print(y_half)
    length = len(y_half[0])
    #print(d)
    x1 = y_half[0][int(length/4)]
    x2 = y_half[0][int(length*3/4)]
    width = x[x2]-x[x1]
    print(f'd2: {d}, width: {width}, height: {height}, ratio: {height/width}')




def output_urls(parametrs, X, output,labl):
    save_file = np.vstack([[parametrs['wit'], 'R', 'T', 'OD'], np.array([X,output['R'],output['T'],output['OD']]).transpose()])

    filename = str(time.time()) +'.csv'
    csv_path = 'app/static/plot/'+filename

    np.savetxt(csv_path, save_file, delimiter = ";", fmt = '%s')
    if labl == '':
        labl = title_to_str(parametrs['title'])
    output_url[labl]=filename
    return output_url


def labels_good(title,parametrs, height, teta): #angle, height, n0, n_last
    labels = {} #str??
    aol = parametrs['amountoflayers']

    for key, d in title['d'].items():
        if d == None:
            labels['d'+str(key)]=height[key]
    if title['n'][aol] == None:
        labels['n_last'] = parametrs['n'][aol]

    if (title['angle']==None) & (parametrs['wit'] != 'angle'):
        labels['angle'] = round(teta*360/(2*pi),2)

    labels = str(labels)[1:-1]
    return(labels)



def title_to_str(title): #dict title to string
    str_title = ''
    try:
        str_title += str(title['material'])[1:-1]+'; '
    except:
        pass
    for i,n in title['n'].items():
        if n != None:
            str_title += f"n{i}: {n}; " #+{k}j
    str_title += '\n'
    for key, item in title.items():
        if (item==None) or (key=='d') or (key=='n') or (key=='material'):
            continue
        str_title += f"{key}: {item}; "
    for i, d in title['d'].items():
        if d != None and d!=0:
            str_title += f"d{i}: {d} nm; "

    return str_title


def calculation(parametrs):
    global output_url
    output_url = {}
    aol = parametrs['amountoflayers']
    n_last = parametrs['n'][aol]
    d = parametrs['d']
    for n_aol in n_last:
        parametrs['n'][aol] = n_aol
        wv,output = het(d,parametrs)

    plt.ylabel(ylab[parametrs['y_label']])
    str_title = title_to_str(parametrs['title'])
    plt.title(str_title)
    plt.legend( ) #title = parametrs['title']
    filename_plot = str(int(time.time())) +'.png'
    image_path = 'app/static/plot/'+filename_plot
    plt.savefig(image_path)


    plt.clf() #delete plot
    return(wv,output,filename_plot)
#plt.show()

# figfile  =  BytesIO() #save in byte, not in file
# plt.savefig(figfile, format = 'png')
# figfile.seek(0)  # rewind to beginning of file
# figdata_png  =  figfile.getvalue()
# image_path  =  base64.b64encode(figdata_png)


# if __name__ == '__main__':
# 	dts = [datas('Al')]#,]
# 	aol = len(dts)+1
# 	aol = 3
# 	wv,n,k = interpolate(dts)

# 	angle = np.arange(1.3,1.57,0.03)
# 	d = {1:[10], 2:[10,20],3:[0]}

# 	n[0],n[aol] = 2.3,[1]
# 	k[0],k[aol] = 0,0

# 	labels = {}


# 	parametrs['d'] = d
# 	#parametrs = {'wv':wv, 'n':n, 'k':k, 'd':d, 'angle':angle,  'amountoflayers':aol, 'y':'R', 'labels':{}}
# 	parametrs['title'] = titles(**parametrs)

# 	for n_aol in n[aol]:
# 		parametrs['n'][aol] = n_aol
# 		het(d,parametrs)
# 	plt.ylabel(ylab[parametrs['y_label']])
# 	plt.title(parametrs['title'])
# 	plt.legend()
# 	plt.show()




