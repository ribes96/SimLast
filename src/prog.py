#!/usr/bin/python3
# -*- coding: utf-8 -*-


import aux
import random
import uuid

exec_info = []
# cada posición de esta lista contiene toda la información de
# una de las ejecuciones

actual_exec = 0
# esta valor se irá incrementando a medida que hagamos cada una
# de las ejecuciones
actual_step = 0
# indica el step en el que nos encontramos en la ejecución acutal

people = []
# contiene a las personas que existen en la ejecución actual

buses = []

#crea una persona nueva, la inicializa adecuadamente
# y actualiza también la estación en la que aparece
def generate_person():
    global actual_step
    global people
    global buses
    person = {}
    origdest = random.sample(range(0,len(aux.stations)),2)
    origdest = sorted(origdest)
    person['orig'] = origdest[0]
    person['dest'] = origdest[1]
    # estos números indican el número de estación, no la
    #posición en el recorrido
    person['spawn_time'] = actual_step
    person['status'] = 'waiting'
    person['id'] = uuid.uuid4()
    people.append(person)
    aux.stations[person['orig']]['people'].append(person)

def generate_bus():
    global buses
    global people
    global actual_step
    bus = {}
    bustype = random.uniform(0,1)
    actype = 0.0
    for postype in aux.params['buses']:
        if actype + postype['proportion'] >= bustype and actype <= bustype:
            bus['capacity'] = postype['capacity']
        actype += postype['proportion']
    bus['people'] = []
    bus['steps'] = []
    #esto es una lista que contiene todos los steps de ejecución
    #para cada step guardará toda la información necesaria
    bus['act_pos'] = 0
    bus['state'] = 'running'
    bus['num_pass'] = 0
    # la cantidad de autobuses a los que ha adelantado
    # bus
    # TODO inicializar una lista con el timestamp de cuando lllega a una estación

    buses.append(bus)


# retorna (true, y la estación) si en esa posición hay una parada,
# y (false,none) en caso contrario
def pos_is_station(pos):
    global people
    global buses
    global actual_step
    for stat in aux.stations:
        if stat['pos'] == pos:
            return (True, stat)
        if stat['pos'] > pos:
            return (False, None)
    return (False, None)


# pone a la persona que se identifica como id
# en el estado done
def set_done(iden):
    global people
    global buses
    global actual_step
    for person in people:
        if person['id'] == iden:
            person['status'] = 'done'
            break

# pone a la persona que se identifica como id
# en el estado done
def set_going(iden):
    global people
    global buses
    global actual_step
    for person in people:
        if person['id'] == iden:
            person['status'] = 'going'
            break

# pone a la persona que se identifica como id
# en el estado done
def set_up_time(iden,up_time):
    global people
    global buses
    global actual_step
    for person in people:
        if person['id'] == iden:
            person['up_time'] = up_time
            break

#Hace que bajen las personas que se bajan en esta parada
def people_down(bus):
    global people
    global actual_step
    global buses
    for person in bus['people'][:]:
        if aux.stations[person['dest']]['pos'] == bus['act_pos']:
            bus['people'].remove(person)
            person['status'] = 'done'
            set_done(person['id'])

#hace que una de las personas que están
#esperando al autobús suba
# se entiende que subirá la primera que haya en la
#lista, y a esta la quitaramos
def one_person_up(bus,stat):
    global actual_step
    global people
    global buses
    if not stat['people']:
        return
    person = stat['people'][0]
    person['status'] = 'going'
    set_going(person['id'])
    person['up_time'] = actual_step
    set_up_time(person['id'],actual_step)
    # el momento en el que ha podido subir al autobús
    bus['people'].append(person)
    stat['people'].pop(0)


def action_bus_in_station(bus,stat):
    global people
    global buses
    global actual_step
    people_down(bus)
    if aux.params['people_freq'] <= 1:
        num_people_up = 1 / aux.params['people_freq']
        int_num_people_up = int(num_people_up)
        diff = num_people_up - int_num_people_up;
        if random.uniform(0,1) <= diff:
            int_num_people_up += 1
        for i in range(0,int_num_people_up):
            one_person_up(bus,stat)
    else:
        part = int(aux.params['people_freq'])
        if actual_step % part == 0:
            one_person_up(bus,stat)

def is_station_in_range(pre, post):
    global people
    global buses
    global actual_step
    for stat in aux.stations:
        if stat['pos'] > pre and stat['pos'] <= post:
            return (True, stat['pos'])
    return (False, None)

def bus_save_step(bus):
    global people
    global buses
    global actual_step
    step_data = {}
    step_data['pos'] = bus['act_pos']
    step_data['ocupation'] = len(bus['people'])
    bus['steps'].append(step_data)

# Hace que cada uno de los autobuses guarde sus steps
def save_steps():
    global people
    global buses
    global actual_step
    for bus in buses:
        bus_save_step(bus)

def step():
    global actual_step
    global buses
    global people
    # print("El valor de actual_step es", actual_step)
    if actual_step % aux.params['bus_freq'] == 0:
        generate_bus()
    if aux.params['people_freq'] > 0 and aux.params['people_freq'] <= 1:
        people_to_generate = 1 / aux.params['people_freq']
        int_people = int(people_to_generate)
        prob = people_to_generate - int_people
        if prob >= random.uniform(0,1):
            int_people += 1
        for i in range(0,int_people):
            generate_person()
    elif aux.params['people_freq'] > 1:
        int_steps = int(aux.params['people_freq'])
        remain_steps = aux.params['people_freq'] - int_steps
        period = (actual_step % int_steps )/int_steps
        diff = abs(remain_steps - period)
        # de momento vamos a hacer solo los enteros
        if actual_step % int_steps == 0:
            generate_person()
        # if random.uniform(0,1) >= diff:
        #     print("Ha tocado generar una persona")
        #     generate_person()
    for bus in buses:
        if bus['state'] == 'ended':
            continue
        tup = pos_is_station(bus['act_pos'])
        if tup[0]:
            action_bus_in_station(bus,tup[1])
            if not tup[1]['people']:
                ootup = is_station_in_range(bus['act_pos'], bus['act_pos'] + aux.params['bus_speed'])
                if ootup[0]:
                    bus['act_pos'] = ootup[1]
                else:
                    bus['act_pos'] += aux.params['bus_speed']
                if bus['act_pos'] > aux.stations[len(aux.stations)-1]['pos']:
                    bus['state'] = 'ended'
        otup = is_station_in_range(bus['act_pos'], bus['act_pos'] + aux.params['bus_speed'])
        if otup[0]:
            bus['act_pos'] = otup[1]
        else:
            bus['act_pos'] += aux.params['bus_speed']

    save_steps()
    actual_step += 1

#retorna una tupla con la media de espera que han tenido
#las personas junto con el máximo
def get_exec_data_people():
    global people
    global buses
    global actual_step
    em = -1
    suma = 0
    amount = 0
    for person in people:
        if person['status'] != 'waiting':
            espera = person['up_time'] - person['spawn_time']
            suma += espera
            amount += 1
            if espera > em:
                em = espera
    media = suma / amount
    return (media, em)

#retorna
#(suma ocupacines, cantidad de checks, cantidad de sobrepases, máxima ocup)
def bus_exec_data_journey(bus):
    mo = -1
    suma = 0
    total = 0
    amount_pass = 0
    for step_data in bus['steps']:
        ocup = step_data['ocupation']
        suma += ocup
        total += 1
        if ocup > bus['capacity']:
            amount_pass += 1
        if ocup > mo:
            mo = ocup
    return (suma, total, amount_pass, mo)


#retorna una tupla que contiene
#la ocupación media, la máxima i la cantidad de veces que se ha
#superado la capacidad
def get_exec_data_journey():
    global people
    global buses
    global actual_step
    suma = 0
    num_checks = 0
    amount_pass = 0
    max_ocup = -1
    for bus in buses:
        tupa = bus_exec_data_journey(bus)
        suma += tupa[0]
        num_checks += tupa[1]
        amount_pass += tupa[2]
        if tupa[3] > max_ocup:
            max_ocup = tupa[3]
    return (suma / num_checks, max_ocup, amount_pass)

def outresuts(execData, i):
    path = 'output/exec' + str(i) + '.txt'
    oufile = open(path, 'w')
    oufile.write("Mitjana de temps d'espera:" + str(execData['wait_average']) + "\n")
    oufile.write("Màxim temps d'espera: " +  str(execData['wait_max']) + "\n")
    oufile.write("Mitjana d'ocupació: " +  str(execData['ocup_average']) + "\n")
    oufile.write("Màxim d'ocupació: " + str(execData['ocup_max']) + "\n")
    oufile.write("Superació de capacitat màxima: " + str(execData['num_ocup_over']) + "\n")


def one_execution(i):
    global actual_step
    global buses
    global people

    actual_step = 0
    buses = []
    people = []

    while actual_step < aux.params['exec_steps']:
        step()
        #aquí faltaría recoger los datos de cada uno de los steps
    #y aquí faltaría recoger los datos de toda la ejecución
    # print("Hemos terminado de hacer todos los steps, y todo ha queado así")
    # print("personas:")
    # for person in people:
    #     print(person)
    #     print("----------")
    tupa = get_exec_data_people()
    tupa2 = get_exec_data_journey()
    execData = {}
    execData['wait_average'] = tupa[0]
    execData['wait_max'] = tupa[1]
    execData['ocup_average'] = tupa2[0]
    execData['ocup_max'] = tupa2[1]
    execData['num_ocup_over'] = tupa2[2]
    print("La media de esperar ha sido ", tupa[0])
    print("La espera máxima ha sido de ", tupa[1])
    print("La media de ocupación ha sido ", tupa2[0])
    print("La ocupación máxima ha sido de ", tupa2[1])
    print("La cantidad de veces que se ha superado la capacidad máxima es de ", tupa2[2])
    outresuts(execData, i)




aux.readStations()
aux.readParams()
for i in range(1,aux.params['num_exec']):
    one_execution(i)
