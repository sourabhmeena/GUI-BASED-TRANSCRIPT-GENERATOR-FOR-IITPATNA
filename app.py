import flask
from fpdf import FPDF
from logging import debug
from flask import Flask,render_template,request,session,flash
from datetime import date 
import csv 
import os

unexist_stud=[]
app = Flask(__name__)
app.secret_key='super-secret-key'

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/Return",methods=['GET','POST'])
def Return():
    return render_template("index.html")


@app.route("/download",methods=['GET','POST'])
def downlaod():
    return render_template("download.html",len= len(unexist_stud),unexist_stud=unexist_stud)
#Transcript generator .....    
class PDF(FPDF):
    def Transcript_generator(self,roll_no,stud_sem,grade,credit,x_coord,y_coord):
        x=0
        y=0
        total_credit=0
        sem_total_credit=0
        spi=0
        cpi=0
        cal_grade={"AA":10,"AB":9,"BB":8,"BC":7,"CC":6,"CD":5,"DD":4,"F":0,'I':0}
        for sem in stud_sem[roll_no]:
            spi=0
            sem_total_credit=0
            sem_cleared_credit=0
            title='semester '+sem
            #table_heading ::
            self.set_xy(x_coord[x%3],y_coord[y])
            self.set_font("Helvetica",'BU',9)
            self.cell(15,8,title)
            self.ln()
            #body:
            #row-> title:
            row_title={'Sub Code':18,'Subject Name':63,'L-T-P':13,'CRD':13,'GRD':13}
            self.set_x(x_coord[x%3])
            for i in row_title:
                self.set_font("Helvetica",'B',7)
                self.cell(row_title[i],5,i,border=1,align='C')
            self.ln()
            
            for sub_code in stud_sem[roll_no][sem]:
                self.set_x(x_coord[x%3])
                self.set_font("Helvetica",'',7)
                self.cell(18,5,sub_code,border=1,align='C')
                self.cell(63,5,credit[sub_code][0],border=1,align='C')
                self.cell(13,5,credit[sub_code][1],border=1,align='C')
                self.cell(13,5,credit[sub_code][2],border=1,align='C')
                self.cell(13,5,grade[roll_no][sub_code],border=1,align='C') 
                if(cal_grade[grade[roll_no][sub_code]]>0):
                    sem_cleared_credit+=float(credit[sub_code][2])
                sem_total_credit+=float(credit[sub_code][2])
                spi+=(cal_grade[grade[roll_no][sub_code]])*float(credit[sub_code][2])
                self.ln()
            cpi+=spi
            total_credit+=sem_total_credit
            self.ln(4)
            self.set_x(x_coord[x%3]) 
            self.cell(67,5,f"Credits Taken: {sem_total_credit}   Cleared: {sem_cleared_credit}  SPI: {round(spi/sem_total_credit,2)}   CPI: {round(cpi/total_credit,2)}",border=1,align='C')
            x+=1
            if(x%3==0) :
                y+=1

   
        
    def header(self):
        self.rect(10.0, 10.0,400.0,277.0)
        # self.line(10,59,410,59)
        # self.line(10,125,410,125)
        # self.line(10,190,410,190)
        self.line(10,255,410,255)
        # self.line(143.33,59,143.33,255)
        # self.line(276.66,59,276.66,255)

        self.rect(10.0,10.0,37,32)
        self.rect(47.0,10.0,326,32)
        self.rect(373,10.0,37,32)
        #logo 
        self.image(r"image\logo.png",16,12,26,23)
        self.image(r"image\hindi_iitp_name.jpeg",120,10.7,180,9)
        self.image(r"image\logo.png",379,12,26,23)
        self.image(r"image\interim.jpg",12,37,34)
        self.image(r"image\iitp.jpg",106,21,220,11)
        self.image(r"image\transcript.jpg",165,30,70,10)
        self.image(r"image\interim.jpg",375,37,34)

    def intro_area(self,name,roll_no,course="Electrical Engineering"):
        roll_no=roll_no[:4]+roll_no[4:6].upper()+roll_no[6:]
        name=name.upper()
        #roll_no:
        self.rect(90,44,240,14)
        self.image(r'image\roll_no.jpg',94,46,12.3)
        self.set_xy(114,43.4)
        self.set_font('Helvetica','',11.5)
        self.cell(15,8,roll_no,align='L')
        #name:
        self.image(r"image\name.jpg",170,45.7,12)
        self.set_xy(187,43.4)
        self.set_font('Helvetica','',12)
        self.cell(15,8,name,align='L')
        #year of admission:
        year='20'+roll_no[:2]
        self.image(r"image\Year_of_admission.jpg",259,46,35)
        self.set_xy(297,44.2)
        self.set_font('Helvetica','',13)
        self.cell(15,8,year,align='L')
        #Program:
        self.image(r"image\programme.jpg",94,52,19)
        self.set_xy(114,50)
        self.set_font('Helvetica','',13)
        self.cell(15,8,"Bachelor of Technology",align='L')
        #course:
        self.image(r"image\course.jpg",169,52,15)
        self.set_xy(187,50)
        self.set_font('Helvetica','',13)
        self.cell(30,8,course,align='L')

    def footer(self):
        #date of issue::
        self.set_xy(12,265)
        self.set_font("Helvetica",'B',13)
        today=date.today()
        self.cell(15,8,'Date of Issue:  '+today.strftime("%b %d, %Y"))
        
        self.line(12,273,75,273)
        self.set_xy(345,275)
        self.set_font("Times",'',13)
        self.cell(15,8,'Assistant Registrar(Academic):')
        if(os.path.isfile(r'image\stampiitp.jpg')):
            self.image(r'image\stampiitp.jpg',200,257,25,25)
        if(os.path.isfile(r'image\sign.jpeg')):
            self.image(r'image\sign.jpeg',350,257,20,20)
        
#grades.csv----->
@app.route("/grades",methods=['GET','POST'])
def grades():
    if(request.method=="POST"):
            f=request.files['grades_file']
            k=f.filename
            if(k!=''):
                f.save("grades.csv")
                flash("'grades.csv' uploaded")
            else:
                flash("Please Upload file after Selecting")
        
    return render_template("index.html")

#name-roll.csv
@app.route("/names",methods=['GET','POST'])
def names():
    if(request.method=="POST"):
        f=request.files['name-roll']
        k=f.filename
        if(k!=''):
            f.save("names-roll.csv")
            flash("'names.csv' uploaded")
        else:
            flash("Please Upload file after Selecting")
    return render_template("index.html")
#subject_master.csv
@app.route("/master",methods=['GET','POST'])
def master():
    if(request.method=="POST"):
        f=request.files['master_roll']
        k=f.filename
        if(k!=''):
            f.save('subject_master.csv')
            flash("'subject_master.csv' uploaded")
        else:
            flash("Please Upload file after Selecting")
    return render_template("index.html")
#signature
@app.route("/sign",methods=['GET','POST'])
def sign():
    if(request.method=="POST"):
        f=request.files['signature']
        k=f.filename
        if(k!=''):
            f.save(r"image\sign.jpeg")
            flash("file_uploaded")
    return render_template("index.html")
#upload seal-->
@app.route("/seal",methods=['GET','POST'])
def seal():
    if(request.method=="POST"):
        f=request.files['seal']
        k=f.filename
        if(k!=''):
            f.save(r"image\stampiitp.jpg")
            flash("file_uploaded")
    return render_template("index.html")
        

def Transcript(roll_no,stud,stud_sem,grade,credit,x_coord,y_coord):
  
    pdf = PDF("L","mm","A3")
    pdf.set_auto_page_break(False,0)
    pdf.add_page()
    pdf.header()
    #intro area-------------->
    branch={'CS':"Computer Science Engineering",'EE':"Electrical Engineering","ME":"Mechanical Engineering"}
    pdf.intro_area(stud[roll_no],roll_no,branch[roll_no[4:6]])
    pdf.Transcript_generator(roll_no,stud_sem,grade,credit,x_coord,y_coord)
    pdf.footer()
    pdf.output(f'transcriptsIITP\\{roll_no}.pdf','F')


def generate_Transcript_for_given_range(starting,ending , stud,stud_sem,grade,credit,x_coord,y_coord):

    try:
        if(starting[:6] != ending[:6]):
            #error dena h ki same branch daalo;
            return render_template("index.html")
        for value in range(int(starting[6:]),int(ending[6:])+1):
            if(stud.get(starting[:6]+str(value).zfill(2)) !=None):
                roll_no=starting[:6]+str(value).zfill(2)
                # print(roll_no)
                Transcript(roll_no,stud,stud_sem,grade,credit,x_coord,y_coord)
            else:
                unexist_stud.append(starting[:6]+str(value).zfill(2))
        ###return render_template...
    except:
        print('error:')
        #chapna h flash se::
        return 

#data generation of futher use to make table.....
@app.route("/unexist",methods=['GET','POST'])
def unexist():
    if(request.method=="POST"):
        return render_template(r'unexist.html')

@app.route("/generateRange",methods=['GET','POST'])
def generateRange():
    if(request.method=='POST'):
        
        starting=(request.form["starting"]).upper()
        ending=(request.form["ending"]).upper()
        if(starting=="" or ending==""):
            flash("Please Enter Starting and Ending RollNO")
            return render_template("index.html")
        # print(starting," ,",ending)
        stud={}  #[roll no]
        stud_sem={}   #{roll no:{semester: [subject code]}}
        grade={}      # {roll no : {subject :grade}}
        credit={}     # {sub_code: [subject_name,itp,crd]}
        with open("names-roll.csv",'r') as roll:
            head=roll.readline()
            reader=csv.reader(roll)
            for row in reader:
                stud.update({row[0]:row[1]})

        with open("grades.csv",'r') as roll:
            head=roll.readline()
            reader=csv.reader(roll)
            for row in reader:
                if(stud_sem.get(row[0])):
                    if(stud_sem[row[0]].get(row[1])):
                        stud_sem[row[0]][row[1]].append(row[2])
                    else:
                        stud_sem[row[0]].update({row[1]:[row[2],]})
                else:
                    stud_sem.update({row[0]:{row[1]:[row[2],]}})
                #stud_sem.update({row[0]:})
                if(grade.get(row[0])):
                        grade[row[0]].update({row[2]:row[4].strip()})        
                else:
                    grade.update({row[0]:{row[2]:row[4].strip()}})

        with open("subject_master.csv",'r') as roll:
            head=roll.readline()
            reader=csv.reader(roll)
            for row in reader:
                credit.update({row[0]:[row[1],row[2],row[3]]})

        x_coord=[13,147,280]
        y_coord=[62,129,194]        
        generate_Transcript_for_given_range(starting , ending ,stud,stud_sem,grade,credit,x_coord,y_coord)
    flash(f"Marksheet of {starting} to {ending} has been Generated:)")
    return render_template("index.html")



@app.route("/AllMarksheet",methods=['GET','POST'])
def AllMarksheet():
    if(request.method=='POST'):
        stud={}  #[roll no]
        stud_sem={}   #{roll no:{semester: [subject code]}}
        grade={}      # {roll no : {subject :grade}}
        credit={}     # {sub_code: [subject_name,itp,crd]}
        with open("names-roll.csv",'r') as roll:
            head=roll.readline()
            reader=csv.reader(roll)
            for row in reader:
                stud.update({row[0]:row[1]})

        with open("grades.csv",'r') as roll:
            head=roll.readline()
            reader=csv.reader(roll)
            for row in reader:
                if(stud_sem.get(row[0])):
                    if(stud_sem[row[0]].get(row[1])):
                        stud_sem[row[0]][row[1]].append(row[2])
                    else:
                        stud_sem[row[0]].update({row[1]:[row[2],]})
                else:
                    stud_sem.update({row[0]:{row[1]:[row[2],]}})
                #stud_sem.update({row[0]:})
                if(grade.get(row[0])):
                        grade[row[0]].update({row[2]:row[4].strip()})        
                else:
                    grade.update({row[0]:{row[2]:row[4].strip()}})

        with open("subject_master.csv",'r') as roll:
            head=roll.readline()
            reader=csv.reader(roll)
            for row in reader:
                credit.update({row[0]:[row[1],row[2],row[3]]})

        x_coord=[13,147,280]
        y_coord=[62,129,194]        
        for roll_no in stud:     
            pdf = PDF("L","mm","A3")
            pdf.set_auto_page_break(False,0)
            pdf.add_page()
            pdf.header()
            #intro area-------------->
            branch={'CS':"Computer Science Engineering",'EE':"Electrical Engineering","ME":"Mechanical Engineering"}
            pdf.intro_area(stud[roll_no],roll_no,branch[roll_no[4:6]])
            pdf.Transcript_generator(roll_no,stud_sem,grade,credit,x_coord,y_coord)
            pdf.footer()
            pdf.output(f'transcriptsIITP\\{roll_no}.pdf','F')
    flash("All MarkSheet has been generated successfully:)")
    return render_template("index.html")

app.run(debug=True)