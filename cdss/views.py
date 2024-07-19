from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
#from .models import LWGMKNN
import joblib
import pandas as pd
from util.lwgk import LWGMKNN
from django.template import Template, Context
import numpy as np
from django.contrib.sessions.models import Session
from bs4 import BeautifulSoup
import geocoder
import requests
from django.http import HttpRequest
from geopy.geocoders import Nominatim
from django.http import JsonResponse
import json
import urllib.parse

def mainPage(request):
    cookie_value = request.COOKIES.get('csrftoken')
    print(cookie_value)
    template=loader.get_template('cdss1.html')
    return HttpResponse(template.render())

def clientPage(request):
    

    template=loader.get_template('cdss2a.html')
    return HttpResponse(template.render())

# Example usage

#print("City:", city)
def getDoc(city):
    
    #city = get_user_city(user_ip)
    url = "https://curofy.com/doctors/"+city+"/cardiology"
    doc=[]
# Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <a> tags with the specified class
        doctor_links = soup.find_all('a', class_='user-profile-section-name')

        # Extract and print the text content of each <a> tag
        for link in doctor_links:
            doctor_name = link.text.strip()
            doc.append(doctor_name)
   
    else:
        print("Failed to retrieve webpage")
    return doc
#We process the basic details from public  
def fromFirst(request):
    city_data_json = request.COOKIES.get('cityData')
    user_ip = request.META.get('REMOTE_ADDR')
    cookie_value = request.COOKIES.get('csrftoken')
    #print(city_data_json)
    city_data_json_decoded = urllib.parse.unquote(city_data_json)

# Parse the JSON string to extract the city
    city_data = json.loads(city_data_json_decoded)
    city = city_data.get('city')

    print(city)  

    
    d={}
    if(request.method=='POST'):
        
        
        print(request.POST)
        height = (request.POST['height'])
        weight = (request.POST['weight'])
        dbs = (request.POST['dbs'])
        stke = (request.POST['stke'])
        hyp=(request.POST['hyp'])
        
        if not height or not weight or not dbs or not stke or dbs=="Select" or stke=="Select" or hyp=="Select":
            message = "Please fill in all required fields."
            return render(request, 'cdss2a.html', {'message': message})
        x = float(weight)/(float(height)**2)
        

        doc=getDoc(city)
        print(doc)
        request.session['doc'] = doc
        request.session['hyp']=hyp
        request.session['BMI']=x
        request.session['dbs']=dbs
        request.session['stke']=stke
        d = {'BMI': x , 'diabetes': dbs , 'prevalentStroke' : stke,'hyp':hyp}
    return render(request,'cdss2.html', d)
    print()
    #return JsonResponse({'BMI': x , 'diabetes': dbs , 'prevalentStroke' : stke,'rw':'cdss2.html'})
   


#this displays the result

def contactInfo(request):
    status=PublicResult(request)
    #print(status)
    #print("{{}}",status)
    if (type(status)==str):
        hyp=request.session.get('hyp')
        BMI=request.session.get('BMI')
        dbs=request.session.get('dbs')
        stke=request.session.get('stke')
        return render(request,'cdss2.html',{'hyp':hyp,'message':status,'BMI':BMI,'diabetes':dbs,'prevalentStroke':stke,})
    else:
        result={'res':status['real']}
        request.session['presdata']=status
        #data={'data':status['data1']}
        template=loader.get_template('cdss4.html')
        return render(request,'cdss4.html',result)
#this displays lifestyle predictions

def showPublicPres(request):

    Todo=request.session.get('presdata')
    doc=request.session.get('doc')
    Todo['doc']=doc

        
    template = loader.get_template('cdss7.html')
    return render(request,'cdss7.html',Todo)
#This process the input from public

def PublicResult(request):

    if(request.method=='POST'):
        
        #print(request.GET)
        #print(request.POST)
        Gender = request.POST['Gender']
        #print(Gender)
        age =(request.POST)['age']
        prevalentStroke = str((request.POST)['prevalentStroke'])
        prevalentHyp = str(request.POST['prevalentHyp'])
        diabetes = (request.POST)['diabetes']
        totChol = (request.POST['totalCal'])
        sysBP = (request.POST['sysBP'])
        diaBP =(request.POST['diaBP'])
        BMI = (request.POST['BMI'])
        heartRt = (request.POST['heartRt'])
        glucose = (request.POST['glucose'])
        if not age or not prevalentStroke or not prevalentHyp or not diabetes or not totChol or not sysBP or not diaBP or not BMI or not heartRt or not glucose or Gender=="Select":
            message = "Please fill in all required fields."
            return message
        result = getPublicPredictions(Gender,age,prevalentStroke,prevalentHyp,diabetes,float(totChol),float(sysBP),float(diaBP),float(BMI),int(heartRt),int(glucose))
        data = publicPres(Gender,age,float(totChol),float(sysBP),float(diaBP),float(BMI),int(heartRt))
        
        return {"real":result,"data1":data}
#this imports the model and predicts the value

def getPublicPredictions(Gender,age,prevalentStroke,prevalentHyp,diabetes,totChol,sysBP,diaBP,BMI,heartRate,glucose):
    model = joblib.load(open("./dataSetShelf/publicmodel.joblib", 'rb'))
    prepro = joblib.load(open("./dataSetShelf/publicpreprocessing.joblib",'rb'))
    scaled = joblib.load(open("./dataSetShelf/publicrobust_scaler.joblib",'rb'))
    n_var = scaled.transform([[age,totChol,sysBP,diaBP,BMI,heartRate,glucose]])
    se = prepro['se']
    ea = prepro['ea']
    Gender = se.get(Gender)
    prevalentStroke = ea.get(prevalentStroke)
    prevalentHyp = ea.get(prevalentHyp)
    diabetes = ea.get(diabetes)
    c_var = np.array([Gender,prevalentStroke,prevalentHyp,diabetes])
    n_var=n_var.flatten()
    print(n_var)
    print(c_var)
    pub_var = np.concatenate((n_var,c_var))
    print(pub_var)
    prediction = model.predict(pub_var)
    print(prediction)
    if prediction == 1:
        comment = "Your Heart may be at risk for Coronary Artery Disease"
    elif prediction == 0:
        comment = "Your Heart is Healthy"
    else:
        comment = "error" 
    return comment
#this stores the lifestyle predictions based on input
def publicPres(Gender,age,totChol,sysBP,diaBP,BMI,heartRt):
    pres=["Your Blood pressure levels, BMI, and Heart rate is good!",
              "Your cholesterol levels are not good! You can follow the below prescription to maintain cholesterol levels",
              " Do physical activity daily for 30 minutes but do not lift heavy weights",
              "Quit smoking if you are a smoker.",
              "Maintain moderate body weight",
              "Add food diet to your daily life like fruits, vegetables, lean proteins, whole grains",
              "Consult a doctor if you have any family history of heart disease",
              "Get your cholesterol checkup regularly every 6 months"]
    if int(age) < 19 and totChol < 170 and sysBP in range(89,120) and diaBP in range(59,80) and BMI in range(13,25) and heartRt in range(54,111):
        #1
        pres=["Blood Pressure,Cholesterol levels,BMI, and Heart Rates are good!",
              " Continue to maintain the same!"]
    elif int(age) < 19 and totChol in range(125,170) and sysBP in range(115,120) and diaBP in range(60,80) and BMI in range(18.5,24.9) and heartRt in range(60,100):
        #2
        pres=["Your Blood pressure levels, BMI, and Heart rate is good!",
              "Your cholesterol levels are not good! You can follow the below prescription to maintain cholesterol levels",
              " Do physical activity daily for 30 minutes but do not lift heavy weights",
              "Quit smoking if you are a smoker.",
              "Maintain moderate body weight",
              "Add food diet to your daily life like fruits, vegetables, lean proteins, whole grains",
              "Consult a doctor if you have any family history of heart disease",
              "Get your cholesterol checkup regularly every 6 months"]
    elif Gender=='M' and totChol in range(200,239) and sysBP in range(115,120) and diaBP in range(60,80) and BMI < 13 and heartRt in range(60,100):
        #3
        pres=["Your Cholesterol levels, Blood Pressure levels are good, and heart rate is good!",
              " You are underweight! have good food"]
    elif Gender=='F' and totChol in range(200,239) and sysBP in range(115,120) and diaBP in range(60,80) and BMI < 15 and heartRt in range(60,100):
        #4
        pres=["Your Cholesterol levels, Blood Pressure levels are good, and heart rate is good!",
              " You are underweight! have good food"]
    elif totChol in range(125,170) and sysBP in range(115,120) and diaBP in range(60,80) and  (BMI >25 and BMI < 29.9) and heartRt in range(60,100):
        #5
        pres=["Your Cholesterol levels, Blood Pressure levels are good, and heart rate is good!",
              " You are overweight! Reduce your weight through exercise daily for 30 minutes and have a healthy food diet",
              " Avoid all kinds of junk, processed foods"]
    elif totChol in range(125,170) and sysBP in range(115,120) and diaBP in range(60,80) and BMI > 29.9 and heartRt in range(60,100):
        #6
        pres=["Your Cholesterol levels, Blood Pressure levels, and heart rate are good!",
              " You have obesity! Reduce your weight through exercise daily for 30 minutes and have healthy a food diet",
              "Avoid all kinds of junk, processed foods",
              " Drink a good amount of water",
              "Consult the doctor if you have any family history of heart disease"]
    elif int(age) < 19 and totChol in range(125,170) and sysBP in range(115,120) and diaBP in range(60,80) and (BMI >18.5 and BMI < 24.9) and heartRt in range(40,120):
        #7
        pres=["Your Cholesterol levels, Blood Pressure levels, and heart rate are good!",
              " Your resting heart rate levels are not normal!",
              " Contact a doctor and get ECG done for further analysis"]
    elif int(age) in range(19,51) and totChol in range(125,170) and sysBP in range(115,120) and diaBP in range(60,80) and (BMI >18.5 and BMI < 24.9) and heartRt in range(40,120):
        #8
        pres=["Your Cholesterol levels, Blood Pressure levels, and heart rate are good!",
              " Your resting heart rate levels are not normal!",
              " Contact a doctor and get ECG done for further analysis"]
    elif int(age) > 50 and totChol in range(125,170) and sysBP in range(115,120) and diaBP in range(60,80) and (BMI >18.5 and BMI < 24.9) and heartRt in range(50,100):
        #9
        pres=["Your Cholesterol levels, Blood Pressure levels, and heart rate are good!",
              " Your resting heart rate levels are not normal!",
              " Contact a doctor and get ECG done for further analysis"]
    elif int(age) > 19 and totChol in range(125,200) and sysBP in range(115,120) and diaBP in range(60,80) and (BMI >18.5 and BMI < 24.9) and heartRt in range(60,100):
        #10
        pres=["Your Blood pressure levels, BMI, and Heart rate is good!",
        "Your cholesterol levels are not good! You can follow the below prescription to maintain cholesterol levels ",
        "Do physical activity daily for 30 minutes but do not lift heavy weights ",
        "Quit Smoking if you are a smoker ",
        "Maintain moderate body weight ",
        "Add food diet to your daily life like fruits, vegetables, lean proteins, whole grains ",
        "Consult a doctor if you have any family history of heart disease ",
        "Get your cholesterol checkup regularly every 6 months"]
    print(pres)
    return pres
#this loads the clinician page

def clinicalPage(request):
    template=loader.get_template('cdss3.html')
    return HttpResponse(template.render())
#this displays the result

def doctorGets(request):
    status = ClinicianResult(request)
    if(type(status)==str):
        return render(request, 'cdss3.html', {'message': status})
    else:
        result = {'res':status['result']}
        print(status)
        request.session['presdata']=status
        template = loader.get_template('cdss6.html')
        return render(request,'cdss6.html',result)
#this shows the lifestyle predictions

def showClinicianPres(request):
    Todo=request.session.get('presdata')
    print(">>",Todo)
    template = loader.get_template('cdss8.html')
    return render(request,'cdss8.html',Todo)
#this loads the model and gets the prediction

def getClinicianPredictions(Sex,Age,ChestPainType,FastingBS,Cholesterol,RestingBP,Oldpeak,ExerciseAngina,MaxHR,ST_Slope,RestingECG):
    model = joblib.load(open("./dataSetShelf/clinicianmodel.joblib",'rb'))
    prepro = joblib.load(open("./dataSetShelf/clinicianpreprocessing.joblib",'rb'))
    scaled = joblib.load(open("./dataSetShelf/clinicianrobust_scaler.joblib",'rb'))
    n_var = scaled.transform([[Age,RestingBP,Cholesterol,MaxHR,Oldpeak]])
    ss = prepro['ss']
    re = prepro['re']
    se = prepro['se']
    cpt = prepro['cpt']
    ea = prepro['ea']
    ST_Slope = ss.get(ST_Slope)
    RestingECG = re.get(RestingECG)
    Sex = se.get(Sex)
    FastingBS=ea.get(FastingBS)
    ChestPainType = cpt.get(ChestPainType)
    ExerciseAngina = ea.get(ExerciseAngina)
    c_var=np.array([Sex,ChestPainType,FastingBS,ST_Slope,RestingECG,ExerciseAngina])
    n_var=n_var.flatten()
    cli_var = np.concatenate((n_var,c_var))
    print(cli_var)
    prediction = model.predict(cli_var)
    if prediction == 1:
        return "Patient's Heart may be at risk for Coronary Artery Disease"
    elif prediction == 0:
        return "Patient's Heart is Healthy"
    else:
        return "error"
#this gets the input

def ClinicianResult(request):
    Sex = (request.POST['Sex'])
    Age = request.POST['Age']
    ChestPainType = request.POST['ChestPainType']
    FastingBS = str(request.POST['FastingBS'])
    RestingBP = (request.POST['RestingBP'])
    Cholesterol = (request.POST['Cholesterol'])
    ExerciseAngina = str(request.POST['ExerciseAngina'])
    Oldpeak = (request.POST['Oldpeak'])
    RestingECG = str(request.POST['RestingECG'])
    MaxHR = (request.POST['MaxHR'])
    ST_Slope = str(request.POST['ST_Slope'])
    if Sex=="Select" or not Age or ChestPainType=="Select" or FastingBS=="Select" or not RestingBP or not Cholesterol or ExerciseAngina=="Select" or not Oldpeak or RestingECG=="Select" or not MaxHR or  ST_Slope=="Select":
            message = "Please fill in all required fields."
            return message
    result = getClinicianPredictions(str(Sex),int(Age),ChestPainType,FastingBS,int(Cholesterol),float(RestingBP),float(Oldpeak),ExerciseAngina,int(MaxHR),ST_Slope,RestingECG)
    data = clinicianPres(Sex,int(Age),ChestPainType,int(Cholesterol),FastingBS,ExerciseAngina,int(MaxHR),ST_Slope,RestingECG)
    return {'result':result,'data':data}
#this determines the prescription

def clinicianPres(Sex,Age,ChestPainType,Cholesterol,FastingBS,ExerciseAngina,MaxHR,ST_Slope,RestingECG):
    prelist=[]
    data2 =["Maintain Blood pressure and cholesterol levels "]
    if ChestPainType==0:
        data2=["Maintain Blood pressure and cholesterol levels ",
        "Quit smoking ",
        "Maintain Blood sugar levels ",
        "Maintain Body weight ",
        "Maintain a healthy diet ",
        "Involve in Physical activities ",
        "Check for family history of heart diseases ",
        "Contact cardiologist"]
    elif ChestPainType==1:
        data2=["Contact cardiologist ",
        "Quit smoking ",
        "Maintain Body weight ",
        "Maintain a healthy diet ",
        "Start or continue treatment ",
        "Check for family history of heart diseases ",
        "Avoid Stress"]
    elif ChestPainType==2:
        data2=["Maintain a healthy weight ",
        "Avoid tight-fitting clothes ",
        "Avoid caffeine, fried foods, and soft drinks ",
        "Have food 3 hrs. before bed ",
        "Quit smoking ",
        "Avoid soups, creamy or cheesy foods"]
    elif ChestPainType==3:
        data2=["Reduce/maintain healthy foods",
        "Exercise regularly",
        "Maintain Blood pressure levels",
        "Maintain cholesterol levels",
        "Meditate to relieve stress",
        "Quit smoking if you are a smoker",
        "Check for family history of heart diseases",
        "Go for ECG, CT-Scan, and MRI"]
    prelist.extend(data2)

    if (Age<19 and (Cholesterol>170 or Cholesterol<125)) or (Age>19 and (Cholesterol>200 or Cholesterol<125)):
        data3=["Your cholesterol levels are not good! You can follow the below prescription to maintain cholesterol levels ",
        "Do physical activity daily for 30 minutes but do not lift heavy weights ",
        "Quit Smoking if you are a smoker ",
        "Maintain moderate body weight ",
        "Add food diet to your daily life like fruits, vegetables, lean proteins, whole grains Consult a doctor if you have any family history of heart disease ",
        "Get your cholesterol checkup regularly every 6 months"]
        prelist.extend(data3)
    data4=["Reduce alcohol intake if you have the habit of consuming"]
    if FastingBS in range(100,126):
        data4=["You are in the stage of Pre-diabetes ",
        "Exercise regularly ",
        "Maintain Body weight ",
        "Quit smoking if you are a smoker ",
        "Reduce alcohol intake if you have the habit of consuming ",
        "Eat healthy foods"]
    elif FastingBS=='Y':
        data4=["You may have Diabetes ",
        "Exercise regularly ",
        "Maintain Body weight ",
        "Quit smoking if you are a smoker ",
        "Reduce alcohol intake if you have the habit of consuming ",
        "Eat healthy foods ",
        "Get regular checkups for maintaining diabetes level"]
    prelist.extend(data4)
    
    
    
    data5=["Maintain Blood pressure and cholesterol levels "]
    if RestingECG==1:
        data5=["Needs urgent attention! Contact cardiologist immediately"]
    elif RestingECG==0:
        data5=["Your ECG levels are good!"]
    prelist.extend(data5)
    

    if ExerciseAngina=='Y':
        data6=["Quit smoking if you are a smoker ",
        "Maintain blood, sugar, and cholesterol levels ",
        "Perform physical activity slowly ",
        "Practice Yoga for reducing stress and anger ",
        "Need supervision on exercise activity ",
        "Eat heart-healthy foods"]
        prelist.extend(data6)
    
    
    data7=["Maintain Blood pressure and cholesterol levels "]
    if ST_Slope=='Up':
        data7=["ECG levels are normal"]
    else:
        data7=["Needs urgent attention! Contact cardiologist"]
    prelist.extend(data7)

    if (Sex=='M' and MaxHR>220-Age) or (Sex=='F' and MaxHR>226-Age):
        data8=["Do not Over-excecise! Because this may lead to musculoskeletal injury or may put you at riskof heart disease"]
        prelist.extend(data8)

    if (Sex=='M' and MaxHR<220-Age) or (Sex=='F' and MaxHR<226-Age):
        data9=["Your maximum heart rate is in good range!"]
        prelist.extend(data9)

    return prelist



