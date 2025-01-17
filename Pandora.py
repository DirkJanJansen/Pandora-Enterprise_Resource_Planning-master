import os, sys
from math import sqrt
import datetime
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QApplication, QMessageBox
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, create_engine,\
     insert, select, update, func, Boolean

# following rules for annual consumption of items even/odd year per year
# and calculate warehouse inventory value for charts per month

metadata = MetaData()
artikelen = Table('artikelen', metadata,
    Column('artikelID', Integer(), primary_key=True),
    Column('artikelprijs', Float),
    Column('art_voorraad', Float),
    Column('mutatiedatum', String),
    Column('jaarverbruik_1', Float),
    Column('jaarverbruik_2', Float),
    Column('art_min_voorraad', Float),
    Column('bestelsaldo', Float),
    Column('bestelstatus', Boolean),
    Column('reserveringsaldo', Float),
    Column('categorie', Integer),
    Column('art_bestelgrootte', Float))
params_system = Table('params_system', metadata,
    Column('systemID', Integer(), primary_key=True),
    Column('system_value', Integer))
params_finance = Table('params_finance', metadata,
    Column('financeID', Integer(), primary_key=True),
    Column('factor', Float),
    Column('amount', Float))
magazijnvoorraad = Table('magazijnvoorraad', metadata,
    Column('jaarmaand', String, primary_key=True),
    Column('totaal', Float),
    Column('courant', Float),                     
    Column('incourant', Float))
          
engine = create_engine('postgresql+psycopg2://postgres@localhost/bisystem')
con = engine.connect()

def wrongDatabase():
    msg = QMessageBox()
    msg.setStyleSheet("color: black;  background-color: gainsboro")
    msg.setWindowIcon(QIcon('./images/logos/logo.jpg'))
    msg.setIcon(QMessageBox.Critical)
    msg.setText('Old version Database bisystem is installed!\nDelete old and Restore new version\nfor instructions read Install.txt\nfor Linux read LINUX_install.txt')
    msg.setWindowTitle('ENTRY')
    msg.exec_()

try:
    mjaar = int(str(datetime.date.today())[0:4])
    selpar = select([params_system]).where(params_system.c.systemID == 3)
    rppar = con.execute(selpar).first()
except:
    app=QApplication(sys.argv)
    sys.exit(wrongDatabase())
    app.exec_()

if mjaar%2 == 1 and int(rppar[1]) == 0:
    updpar = update(params_system).where(params_system.c.systemID == 3).values(system_value = 1)
    con.execute(updpar)

    selpar1 = select([params_finance]).where(params_finance.c.financeID == 6)
    rppar1 = con.execute(selpar1).first()
    selpar2 = select([params_finance]).where(params_finance.c.financeID == 8)
    rppar2 = con.execute(selpar2).first()
    selart = select([artikelen]).order_by(artikelen.c.artikelID)
    rpartikel = con.execute(selart)

    for row in rpartikel:
        if row[4] > 0:
            mjaar = int(str(datetime.datetime.now())[0:4])
            mbestgr = round(sqrt(2*row[5]*rppar2[2])/(row[1]*rppar1[1]),0)
            mjrverbr = row[4]
            if row[10] == 1 or row[10] == 5:
                minvrd = round(mjrverbr*1/17, 0) # < 3 weeks delivery time
            elif row[10] == 2 or row[10] == 6 or row[10] == 7:
                minvrd = round(mjrverbr*4/17, 0) # < 12 weeks delivery time
            elif row[10] == 3 or row[10] == 8:
                minvrd = round(mjrverbr*8/17, 0) # < 26 weeks delivery time
            elif row[10] == 4 or row[10] == 9:
                minvrd = round(mjrverbr*16/17,0) # < 52 weeks delivery time
            else:
                minvrd = row[6]

            updart = update(artikelen).where(artikelen.c.artikelID == row[0]).\
                values(jaarverbruik_2 = 0, art_min_voorraad = minvrd, art_bestelgrootte = mbestgr)
            con.execute(updart)
elif mjaar%2 == 0 and int(rppar[1]) == 1:
    updpar = update(params_system).where(params_system.c.systemID == 3).values(system_value = 0)
    con.execute(updpar)
    selpar1 = select([params_finance]).where(params_finance.c.financeID == 6)
    rppar1 = con.execute(selpar1).first()
    selpar2 = select([params_finance]).where(params_finance.c.financeID == 8)
    rppar2 = con.execute(selpar2).first()
    selart = select([artikelen]).order_by(artikelen.c.artikelID)
    rpartikel = con.execute(selart)

    for row in rpartikel:
        if row[5] > 0:
            mjaar = int(str(datetime.datetime.now())[0:4])
            mbestgr = round(sqrt(2*row[4]*rppar2[2])/(row[1]*rppar1[1]),0)
            mjrverbr = row[5]
            if row[10] == 1 or row[10] == 5:
                minvrd = round(mjrverbr*1/17, 0) # < 3 weeks delivery time
            elif row[10] == 2 or row[10] == 6 or row[10] == 7:
                minvrd = round(mjrverbr*4/17, 0) # < 12 weeks delivery time
            elif row[10] == 3 or row[10] == 8:
                minvrd = round(mjrverbr*8/17, 0) # < 26 weeks delivery time
            elif row[10] == 4 or row[10] == 9:
                minvrd = round(mjrverbr*16/17,0) # < 52 weeks delivery time
            else:
                minvrd = row[6]

            updart = update(artikelen).where(artikelen.c.artikelID == row[0]).\
                values(jaarverbruik_1 = 0, art_min_voorraad = minvrd, art_bestelgrootte = mbestgr)
            con.execute(updart)

mhjrmnd = str(datetime.date.today())[0:7]                                                  #(this year year-month) yyyy-mm
mvjrmnd = int(str(int(str(datetime.date.today())[0:4])-1)+str(datetime.date.today())[5:7]) #(last year yearmonth) yyyymm
mdbjrmnd = (con.execute(select([func.max(magazijnvoorraad.c.jaarmaand,
                    type_=Integer)])).scalar())     # (last stored year-month) yyyy-mm
if mhjrmnd != mdbjrmnd:
    insdb = insert(magazijnvoorraad).values(jaarmaand = mhjrmnd)
    con.execute(insdb)
    selart = select([artikelen])
    rpart = con.execute(selart)
    mtotaal = 0
    mcourant = 0
    mincourant = 0
    for row in rpart:      
        mtotaal = mtotaal + row[1]*row[2]                       # total value of stock
        if mvjrmnd < int(str(row[3][0:4])+str(row[3])[5:7]):    # see if last transaction less than a year ago
            mcourant = mcourant + row[1]*row[2]
        else:
            mincourant = mincourant + row[1]*row[2]             # last transaction more than a year ago
    updmvrd = update(magazijnvoorraad).where(magazijnvoorraad.c.jaarmaand == mhjrmnd)\
          .values(totaal = int(mtotaal), courant = int(mcourant), incourant = int(mincourant)) 
    # write totals in present year-month
    con.execute(updmvrd)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Windows")
    if sys.platform == "linux":
        os.system("../.usbkbd.sh")
    from login import inlog
    inlog()
    app.exec_()