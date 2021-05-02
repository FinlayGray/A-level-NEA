# NEA Project: Gymnastics Membership System
# Name: Finlay Gray



# import statements
import pygame as pg
import sys
import sqlite3
from sqlite3 import Error
import re
import hashlib
import socket
import threading
import pickle
import os

# initialise pygame
pg.init()

# Setting up variables
SCR_W, SCR_H = pg.display.Info().current_w, pg.display.Info().current_h
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BACKGROUND_COLOUR = (146, 168, 209)
FONT = pg.font.Font(None, 32)
b = pg.image.load('test_back.png')
pic = pg.transform.scale(b, (SCR_W, SCR_H))
font = pg.font.Font('freesansbold.ttf', 32)

COLOUR_INACTIVE = pg.Color('lightskyblue3')
COLOUR_ACTIVE = pg.Color('dodgerblue2')


# regular expression for password check
def password_check(password):
    valid = False
    length_check = re.search('.{8}', password)
    if length_check:
        upper_case_check = re.search('[A-Z]', password)
        if upper_case_check:
            special_check = re.search('\W', password)
            if special_check:
                number_check = re.search('[0-9]', password)
                if number_check:
                    valid = True

    return valid


# Setting up the screen

SCREEN = pg.display.set_mode((SCR_W, SCR_H))


# create sql class which all sql queries run through
class sql:
    def __init__(self):
        pass

    def create_connection(self, db_file):
        con = None
        try:
            con = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        return con

    # use create table if not exists
    def create_table(self, con, instructions):
        try:
            c = con.cursor()
            c.execute(instructions)
        except Error as e:
            print(e)

    # perform a sql command given
    def perform_command(self, con, instructions, data):
        c = con.cursor()
        c.execute(instructions, data)
        con.commit()

    def delete(self, con, table, section, section2, id):
        sql = 'DELETE FROM {} WHERE {}=? AND {}=?'.format(table, section, section2)
        c = con.cursor()
        c.execute(sql, id)
        con.commit()

    # select all values given a certain criteria
    def select_all_value(self, con, table, section, id):
        sql = 'SELECT * FROM {} WHERE {}=?'.format(table, section)
        c = con.cursor()
        c.execute(sql, (id,))
        rows = c.fetchall()
        return rows

    # select a certain value (first) given a certain criteria (section)
    def selectvalue(self, con, first, table, section, id):
        sql = 'SELECT {} FROM {} WHERE {}=?'.format(first, table, section)
        c = con.cursor()
        c.execute(sql, (id,))
        rows = c.fetchall()
        return rows

    def select_all(self, con, table):
        sql = 'SELECT * FROM {}'.format(table)
        c = con.cursor()
        c.execute(sql)
        rows = c.fetchall()
        return rows

    def update(self, con, table, data1, data2, updated):
        sql = 'UPDATE {} SET {}=? WHERE {}=?'.format(table, data1, data2)
        c = con.cursor()
        c.execute(sql, updated)
        con.commit()


# instantiate sql class and set up tables
db = sql()
# create first connection with file
con = db.create_connection('file.db')
# create members table
db.create_table(con, '''CREATE TABLE IF NOT EXISTS members(
                        id integer PRIMARY KEY AUTOINCREMENT,
                        password text NOT NULL,
                        first_name text NOT NULL,
                        last_name text NOT NULL,
                        type text NOT NULL,
                        DOB date NOT NULL,
                        joined_date date NOT NULL,
                        mobile text NOT NULL,
                        medical text NOT NULL,
                        postcode text NOT NULL,
                        gender text NOT NULL,
                        badges text
                        )''')

# create class table
db.create_table(con, '''CREATE TABLE IF NOT EXISTS class(
                        memberid integer NOT NULL,
                        classid integer NOT NULL,
                        FOREIGN KEY (memberid) REFERENCES members (id)
                            ON DELETE CASCADE ON UPDATE NO ACTION,
                        FOREIGN KEY (classid) REFERENCES class_details (classid)
                            ON DELETE CASCADE ON UPDATE NO ACTION)''')

# create class_details table
db.create_table(con, '''CREATE TABLE IF NOT EXISTS class_details(
                        classid integer PRIMARY KEY AUTOINCREMENT,
                        name text NOT NULL,
                        no_days text NOT NULL,
                        MaxKidsInClass integer NOT NULL,
                        kidsInClass integer NOT NULL,
                        days_times text NOT NULL
                        )''')
# create register table
db.create_table(con, '''CREATE TABLE IF NOT EXISTS register(
                        memberid integer NOT NULL,
                        classid integer NOT NULL,
                        day text NOT NULL,
                        present integer NOT NULL,
                        FOREIGN KEY (memberid) REFERENCES members (id)
                            ON DELETE CASCADE ON UPDATE NO ACTION,
                        FOREIGN KEY (classid) REFERENCES class_details (classid)
                            ON DELETE CASCADE ON UPDATE NO ACTION)''')
# create payrate table
db.create_table(con, '''CREATE TABLE IF NOT EXISTS payrate(
                        id integer NOT NULL,
                        pay real NOT NULL,
                        FOREIGN KEY (id) REFERENCES members (id)
                            ON DELETE CASCADE ON UPDATE NO ACTION)''')

# insert automatic admin for first run
try:
    db.perform_command(con, '''INSERT INTO members VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
        0, 'xxxx', 'admin', 'admin', 'admin', '20-09-2002', '20-05-2020', '07455469158', 'N/A', 'TW167PN', '', ''))
except:
    pass

con.close()


# Button Class
class Button:

    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        self.active = active
        self.rect = pg.Rect(x, y, w, h)
        self.pressed = False
        self.colour = colour
        self.text_colour = BLACK
        self.text = text
        self.txt_surface = FONT.render(text, True, self.text_colour)
        self.rect.w = self.txt_surface.get_width() + 10

    def pressed_func(self):
        pass

    def button_handle(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and not self.pressed and self.active:
            # If the user clicked on the button rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the pressed boolean.
                self.pressed = not self.pressed
            else:
                self.pressed = False
        # runs pressed function when the button is clicked on
        if self.pressed:
            self.pressed_func()
            self.pressed = False
            return True

    def draw(self):
        pg.draw.rect(SCREEN, self.colour, self.rect)

        SCREEN.blit(self.txt_surface,
                    (self.rect.x + 5, self.rect.y + (self.rect.h / 2) - (self.txt_surface.get_height() / 2)))


# submit button for login screen
class Submit_Button(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        memberid = login_page.input_boxes[0].text
        id_check = re.match('[0-9]*', str(memberid))
        # hashes password
        password = hashlib.sha256(login_page.input_boxes[1].text.encode('utf-8')).hexdigest()
        # checks if id already has password
        if id_check:
            if password == 'xxxx':
                id_check = False
        send = True
        text = []
        if id_check:
            con = db.create_connection('file.db')
            ids = db.select_all_value(con, 'members', 'id', memberid)
            con.close()
            # searches through all ids to see if any match id and password
            if ids:
                for id in ids:
                    if password == id[1]:
                        send = False
                        # sends user to different pages depending on what member type they are
                        if id[4] == 'gymnast':
                            login_page.active = False
                            gymnast.active = True
                            gymnast.memberid = memberid
                            gymnast_general_screen.days = calender(memberid)
                            for i in range(len(gymnast_general_screen.days)):
                                text = '{}'.format(gymnast_general_screen.days[i])
                                text = text[2:-4]
                                text = font.render(text, True, WHITE)
                                text = [text, (SCR_W * (1 / 8), (SCR_H * ((3) / 16)))]
                                gymnast_general_screen.text.append(text)
                        elif id[4] == 'coach':
                            login_page.active = False
                            coach_base_page.active = True
                            coach_base_page.memberid = memberid
                            coach_base_page.days = calender(memberid)
                            for i in range(len(coach_base_page.days)):
                                text = '{}'.format(coach_base_page.days[i])
                                text = text[2:-4]
                                text = font.render(text, True, WHITE)
                                text = [text, (SCR_W * (1 / 8), (SCR_H * ((i + 3) / 16)))]
                                coach_base_page.text.append(text)
                        elif id[4] == 'admin':
                            login_page.active = False
                            admin_base_page.active = True
        # blits to screen if invalid data is entered
        text = font.render('Enter a vaild ID and password', True, WHITE)
        to_screen = [text, (SCR_W * (6 / 16), SCR_H - 100)]
        if send:
            login_page.text.append(to_screen)

        for i in login_page.input_boxes:
            i.text = i.ori_text
            i.txt_surface = FONT.render(i.text, True, i.colour)
        pg.display.update()


class Close_Button(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        print('bye bye')
        pg.quit()
        sys.exit()


##Takes user to new member page
class New_Member_Button(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        login_page.active = False
        for i in new_password.input_boxes:
            i.text = i.ori_text
            i.txt_surface = FONT.render(i.text, True, i.colour)
        new_password.active = True


# Checks if id has password linked to it
class New_Member_Button_submit(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        id = new_password.input_boxes[0].text
        con = db.create_connection('file.db')
        rows = db.select_all_value(con, 'members', 'id', id)
        if rows:
            for row in rows:
                if row[1] == 'xxxx':
                    new_password.active = False
                    for i in new_password1.input_boxes:
                        i.text = i.ori_text
                        i.txt_surface = FONT.render(i.text, True, i.colour)
                    new_password1.active = True

        con.close()


# if password meets requirements updates database with new password
class New_Member_Button_submit2(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        id = new_password.input_boxes[0].text
        con = db.create_connection('file.db')
        rows = db.select_all_value(con, 'members', 'id', id)
        pass1 = new_password1.input_boxes[0].text
        pass2 = new_password1.input_boxes[1].text
        send = False
        text = font.render('You have not entered a valid Password', True, WHITE)

        to_screen = [text, ((SCR_W * (1 / 2)) - (text.get_width() / 2), SCR_H - 100)]
        if pass1 == pass2:
            password = password_check(pass1)
            if password:
                for row in rows:
                    # update function
                    # hashes password so it is stored as a hash
                    p = hashlib.sha256(pass1.encode('utf-8')).hexdigest()

                    db.update(con, 'members', 'password', 'id', (p, id))
                    new_password1.active = False
                    login_page.active = True

            else:
                send = True
        else:
            send = True
        if send:
            new_password1.text.append(to_screen)

        con.close()
        login_page.text = []
        new_password1.text = [new_password1.pass_text_help_to_screen]


# sends user back to screen linked via a back_relationships dictionary
class Back_Button(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        go = False
        for i in back_relationships.keys():
            if i.active == True:
                to_back = i
                go = True
        if go:
            to_back.active = False
            for i in back_relationships[to_back].input_boxes:
                i.text = i.ori_text
                i.txt_surface = FONT.render(i.text, True, i.colour)
            back_relationships[to_back].active = True


# Admin page buttons

# takes user to add member screen
class add_member(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        admin_base_page.active = False
        create_member_screen.active = True
        create_member_screen.submit.active = False
        create_member_screen.next.active = True


# add member button submit

class add_member_submit(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        input_text = []
        for i in create_member_screen.input_boxes:
            input_text.append(i)
        con = db.create_connection('file.db')
        # inserts data from text boxes into table members
        db.perform_command(con,
                           'INSERT INTO members(first_name,last_name,password,type,DOB,joined_date,mobile,medical,postcode,gender,badges) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                           (input_text[0].text, input_text[1].text, 'xxxx', input_text[2].text, input_text[3].text,
                            input_text[4].text,
                            input_text[5].text, input_text[6].text, input_text[7].text, input_text[8].text, ','))
        # blits id number just created onto the admin base screen
        c = con.cursor()
        c.execute('SELECT * FROM members ORDER BY id DESC LIMIT 1')
        rows = c.fetchall()
        con.close()
        data = rows[0]

        id_number = data[0]

        text = font.render('Most recent ID number:' + str(id_number), True, WHITE)
        to_screen = [text, (SCR_W * (2 / 6), SCR_H * (1 / 16))]
        admin_base_page.text = []
        admin_base_page.text.append(to_screen)
        for i in create_member_screen.input_boxes:
            i.text = i.ori_text
            i.txt_surface = FONT.render(i.text, True, i.colour)
            if i.show == True:
                i.show = False
            elif i.show == False:
                i.show = True
        create_member_screen.active = False
        admin_base_page.active = True


# allows the user to enter more details
class add_member_next(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        for i in create_member_screen.input_boxes:
            if i.show == True:
                i.show = False
            elif i.show == False:
                i.show = True
        create_member_screen.submit.active = True
        create_member_screen.next.active = False


class add_class_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        admin_base_page.active = False
        create_class_screen.active = True
        create_class_screen.next.active = True
        create_class_screen.submit.active = False


# button that sets up input boxes depending on the number of days the class runs.
class add_class_next(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        for i in create_class_screen.input_boxes:

            if i.show == True:
                i.show = False

        no_days = int(create_class_screen.input_boxes[1].text)
        for i in range(1, no_days + 1):
            day = InputBox((SCR_W / 4) - 100, (SCR_H * (i / 8)), 100, 30, 'enter day', True)
            time = InputBox((SCR_W * (3 / 4)) - 100, (SCR_H * (i / 8)), 100, 30, 'enter time in format start time-end time', True)
            create_class_screen.input_boxes.append(day)
            create_class_screen.input_boxes.append(time)
        create_class_screen.next.active = False
        create_class_screen.submit.active = True


# Take all values from input boxes and put into table
class add_class_submit(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):

        day_time = ''
        for i in range(3, 3 + (len(create_class_screen.input_boxes) - 3), 2):
            day = create_class_screen.input_boxes[i].text
            time = create_class_screen.input_boxes[(i + 1)].text
            day_time += day + '/' + time + ','
        con = db.create_connection('file.db')
        db.perform_command(con,
                           '''INSERT INTO class_details(name,no_days,MaxKidsInClass,kidsInClass,days_times) VALUES(?,?,?,?,?)''',
                           (create_class_screen.input_boxes[0].text, create_class_screen.input_boxes[1].text,
                            create_class_screen.input_boxes[2].text, 0, day_time))
        to_remove = []
        con.close()
        for i in create_class_screen.input_boxes:
            i.text = i.ori_text
            i.txt_surface = FONT.render(i.text, True, i.colour)
            if i.show == True:
                i.show = False
                to_remove.append(i)
            elif i.show == False:
                i.show = True

        # removes all input boxes just created to allow the button to be pressed again
        for i in to_remove:
            create_class_screen.input_boxes.remove(i)

        # reset
        admin_base_page.active = True
        create_class_screen.active = False


# takes user to the add to class screen
class add_to_class_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        admin_base_page.active = False
        add_to_class_screen.class_id = []
        add_to_class_screen.classes = []
        add_to_class_screen.buttons = [add_to_class_screen.back_button, add_to_class_screen.close_button,
                                       add_to_class_screen.next]
        add_to_class_screen.next.active = True
        add_to_class_screen.input_boxes[0].show = True
        add_to_class_screen.active = True


# Button which when pressed adds the member id specified in last screen to class which name is the same as the name
# of the button
class class_name_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):

        class_name = self.text
        member_Id = add_to_class_screen.id_search.text
        con = db.create_connection('file.db')
        data = db.select_all_value(con, 'class_details', 'name', class_name)
        data = data[0]
        num_kids = data[4]
        # increases the number in the class by 1
        num_kids += 1
        db.update(con, 'class_details', 'kidsInClass', 'classid', (num_kids, data[0]))
        db.perform_command(con, '''INSERT INTO class VALUES(?,?)''', (member_Id, data[0]))
        con.close()
        # resets to allow function to be run again
        for i in add_to_class_screen.input_boxes:
            i.text = i.ori_text
            i.txt_surface = FONT.render(i.text, True, i.colour)
            if i.show == True:
                i.show = False
            elif i.show == False:
                i.show = True
        #for i in add_to_class_screen.buttons:
         #   if i.active == True:
          #      i.active = False
           # elif i.active == False:
            #    i.active = True

        add_to_class_screen.active = False
        admin_base_page.active = True


# Present button in take register
class yes_button_reg(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        # sets colour green if pressed
        self.colour = GREEN
        # checks if absent button is green, if so then it goes back to original colour
        for i in range(3, len(register_show_screen.buttons), 2):
            if register_show_screen.buttons[i].colour == GREEN:
                register_show_screen.buttons[i + 1].colour = COLOUR_ACTIVE


# Absent button in take register
class no_button_reg(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        self.colour = GREEN
        for i in range(3, len(register_show_screen.buttons), 2):
            if register_show_screen.buttons[i + 1].colour == GREEN:
                register_show_screen.buttons[i].colour = COLOUR_ACTIVE


# button which allows you to pick the time you want to take the register of.
class pick_day_reg(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        register_screen.buttons = [register_screen.close_button, register_screen.back_button]
        class_name = self.text
        register_show_screen.class_name = class_name
        classes_screen.active = False
        register_screen.active = True
        con = db.create_connection('file.db')
        data = db.selectvalue(con, 'days_times', 'class_details', 'name', class_name)
        con.close()
        data = data[0]
        data = data[0]
        days = data.split(',')
        days.pop(-1)
        for i in range(len(days)):
            but = classes_reg_but((SCR_W / 2) - 100, ((SCR_H * ((i % 8) / 8)) + 25), 50, 30, days[i], True)
            register_screen.buttons.append(but)
        register_show_screen.text = []
        register_show_screen.links = []
        register_show_screen.buttons = [register_show_screen.close_button, register_show_screen.back_button,
                                        register_show_screen.submit_button]


# Prints all the gymnasts in the class out as a list with 2 button linked to each one to allow them to be present
# or absent

class classes_reg_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        # grabs name of day and name of class
        day = self.text
        register_show_screen.day = day
        class_name = register_show_screen.class_name
        # searches for this classes id
        con = db.create_connection('file.db')
        data = db.selectvalue(con, 'classid', 'class_details', 'name', class_name)
        data = data[0]
        data = data[0]
        register_show_screen.classid = data
        register_screen.active = False
        # searches for all member ids with this classid
        ids = []
        ids_raw = db.selectvalue(con, 'memberid', 'class', 'classid', data)

        for i in ids_raw:
            for j in i:
                ids.append(j)
        details = []
        for i in ids:
            data = db.select_all_value(con, 'members', 'id', i)
            try:
                details.append(data[0])
            except:
                pass
        # separates chosen members into gymnasts and coaches
        con.close()
        gymnasts = []
        coaches = []
        for i in details:
            if i[4] == 'gymnast':
                gymnasts.append(i)
            else:
                coaches.append(i)
        count = 1
        font = pg.font.Font('freesansbold.ttf', 16)
        # creates text and 2 buttons for each gymnast
        for i in gymnasts:
            yes = yes_button_reg((SCR_W * 2 / 3), (SCR_H * (count / (SCR_H // 30))), 50, 25, 'Present', True)
            no = no_button_reg((SCR_W * 2 / 3 + 100), (SCR_H * (count / (SCR_H // 30))), 50, 25, 'Absent', True)
            register_show_screen.buttons.append(yes)
            register_show_screen.buttons.append(no)
            stri = i[2] + ' ' + i[3]
            text = font.render(stri, True, WHITE)
            text_to_screen = [text, (SCR_W * (1 / 3), (SCR_H * (count / (SCR_H // 30))))]
            register_show_screen.text.append(text_to_screen)
            register_show_screen.links.append([i[0], yes])

            count += 1

        register_show_screen.active = True


# takes the status of the gymnast as edited when taking register and saves them to the database
class register_submit(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        con = db.create_connection('file.db')

        for i in register_show_screen.links:
            try:
                db.delete(con, 'register', 'classid', 'memberid', (register_show_screen.classid, i[0]))
            except:
                pass
            if i[1].colour == GREEN:
                db.perform_command(con, '''INSERT INTO register VALUES(?,?,?,?)''',
                                   (i[0], register_show_screen.classid, register_show_screen.day, 1))
            else:
                db.perform_command(con, '''INSERT INTO register VALUES(?,?,?,?)''',
                                   (i[0], register_show_screen.classid, register_show_screen.day, 0))
        con.close()
        register_show_screen.active = False
        back_relationships[classes_screen].active = True


# allows you to pick which class you want to view
class view_register(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        if admin_base_page.active == True:
            back_relationships[reg_view_1_screen] = admin_base_page
            admin_base_page.active = False
        elif coach_base_page.active == True:
            back_relationships[reg_view_1_screen] = coach_base_page
            coach_base_page.active = False
        reg_view_1_screen.active = True
        reg_view_2_screen.buttons = [reg_view_2_screen.back_button, reg_view_2_screen.close_button]
        con = db.create_connection('file.db')
        rows = db.select_all(con, 'class_details')
        con.close()
        for row in rows:
            reg_view_1_screen.classes.append(row)
        width = 0
        for i in range(len(reg_view_1_screen.classes)):
            if i % 8 == 0:
                width += 1 / 4

            name = reg_view_1_screen.classes[i][1]

            but = pick_day_view((SCR_W * width) - 100, ((SCR_H * ((i % 8) / 8)) + 25), 50, 30, name, True)
            reg_view_1_screen.buttons.append(but)

        reg_view_1_screen.classes = []


# allows you to pick which day you want to view
class pick_day_view(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        #reg_view_1_screen.buttons = [reg_view_1_screen.close_button, reg_view_1_screen.back_button]
        class_name = self.text
        reg_view_1_screen.class_name = class_name
        reg_view_1_screen.active = False
        reg_view_2_screen.active = True
        con = db.create_connection('file.db')
        data = db.selectvalue(con, 'days_times', 'class_details', 'name', class_name)
        con.close()
        data = data[0]
        data = data[0]
        days = data.split(',')
        days.pop(-1)
        for i in range(len(days)):
            but = view_reg_final((SCR_W / 2) - 100, ((SCR_H * ((i % 8) / 8)) + 25), 50, 30, days[i], True)
            reg_view_2_screen.buttons.append(but)
        reg_view_1_screen.text = []
        reg_view_2_screen.text = []
        #reg_view_1_screen.buttons = [reg_view_1_screen.close_button, reg_view_1_screen.back_button]


# Prints the gymnasts to the screen if a register has been taken as well and whether they were present or absent.
class view_reg_final(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        day = self.text
        reg_view_2_screen.day = day
        class_name = reg_view_1_screen.class_name
        con = db.create_connection('file.db')
        data = db.selectvalue(con, 'classid', 'class_details', 'name', class_name)
        data = data[0]
        data = data[0]
        reg_view_1_screen.classid = data
        ids = []
        ids_raw = db.selectvalue(con, 'memberid', 'class', 'classid', data)
        for i in range(2, len(reg_view_2_screen.buttons)):
            reg_view_2_screen.buttons[i].active = False

        for i in ids_raw:
            for j in i:
                ids.append(j)
        details = []
        for i in ids:
            data = db.select_all_value(con, 'members', 'id', i)
            try:
                details.append(data[0])
            except:
                pass
        gymnasts = []
        coaches = []
        for i in details:
            if i[4] == 'gymnast':
                gymnasts.append(i)
            else:
                coaches.append(i)

        count = 1
        font = pg.font.Font('freesansbold.ttf', 16)
        for i in gymnasts:
            stri = i[2] + ' ' + i[3]
            text = font.render(stri, True, WHITE)
            text_to_screen = [text, (SCR_W * (1 / 3), (SCR_H * (count / (SCR_H // 30))))]
            reg_view_2_screen.text.append(text_to_screen)
            data = db.select_all_value(con, 'register', 'memberid', i[0])
            for i in data:
                if i[1] == reg_view_1_screen.classid:
                    if day in i[2]:
                        if i[3] == 1:
                            text = font.render('Present', True, WHITE)
                        elif i[3] == 0:
                            text = font.render('Absent', True, WHITE)
                        text_to_screen = [text, (SCR_W * (2 / 3), (SCR_H * (count / (SCR_H // 30))))]
                        reg_view_2_screen.text.append(text_to_screen)

            count += 1

        con.close()


# checks all the possible classes the id could be aadded to and puts them on teh screen as buttons
class add_to_class_id_next(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        con = db.create_connection('file.db')
        rows = db.select_all(con, 'class_details')
        con.close()
        for row in rows:
            if row[4] < row[3]:
                add_to_class_screen.classes.append(row)
        for i in add_to_class_screen.input_boxes:
            if i.show == True:
                i.show = False
            elif i.show == False:
                i.show = True
        width = 0
        for i in range(len(add_to_class_screen.classes)):
            if i % 8 == 0:
                width += 1 / 4

            name = add_to_class_screen.classes[i][1]

            if width % 1 == 0:
                but = class_name_but((SCR_W * width) - 100, ((SCR_H * ((i % 8) / 8)) + 25), 50, 30, name, False)
            else:

                but = class_name_but((SCR_W * width) - 100, ((SCR_H * ((i % 8) / 8)) + 25), 50, 30, name, True)
            add_to_class_screen.buttons.append(but)

        add_to_class_screen.next.active = False


class all_members_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        edit_first_screen.active = False
        all_members_screen.active = True
        db.create_connection('file.db')
        data = db.select_all(con,'members')
        for i in range(len(data)):
            text = font.render('{} {} {}'.format([data[i][0],data[i][2],data[i][3]],WHITE, True))
            text_to_screen = [text, (SCR_W * (2 / 3), (SCR_H * (i / (SCR_H // 30))))]
            all_members_screen.text.apppend(text_to_screen)
        con.close()



# puts all the classes that can be registered on the screen as buttons
class classes_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        if admin_base_page.active == True:
            back_relationships[classes_screen] = admin_base_page
            admin_base_page.active = False
        elif coach_base_page.active == True:
            back_relationships[classes_screen] = coach_base_page
            coach_base_page.active = False
        classes_screen.active = True
        con = db.create_connection('file.db')
        rows = db.select_all(con, 'class_details')
        con.close()
        for row in rows:
            classes_screen.classes.append(row)
        width = 0
        for i in range(len(classes_screen.classes)):
            if i % 8 == 0:
                width += 1 / 4

            name = classes_screen.classes[i][1]

            if width % 1 == 0:
                but = pick_day_reg((SCR_W * width) - 100, ((SCR_H * ((i % 8) / 8)) + 25), 50, 30, name, False)
                classes_screen.next_screen.append(but)
            else:
                but = pick_day_reg((SCR_W * width) - 100, ((SCR_H * ((i % 8) / 8)) + 25), 50, 30, name, True)
            classes_screen.buttons.append(but)

        classes_screen.classes = []


# puts all the classes that can be edited on the screen as buttons
class edit_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        admin_base_page.active = False
        edit_first_screen.active = True
        con = db.create_connection('file.db')
        rows = db.select_all(con, 'class_details')
        con.close()
        for row in rows:
            edit_first_screen.classes.append(row)
        width = 0
        for i in range(len(edit_first_screen.classes)):
            if i % 8 == 0:
                width += 1 / 4

            name = edit_first_screen.classes[i][1]

            if width % 1 == 0:

                but = class_choose((SCR_W * width) - 100, ((SCR_H * ((i % 8) / 8)) + 25), 50, 30, name, False)

            else:

                but = class_choose((SCR_W * width) - 100, ((SCR_H * ((i % 8) / 8)) + 25), 50, 30, name, True)
            edit_first_screen.buttons.append(but)

        edit_first_screen.classes = []


# saves the class id and name of the class you want to edit
class class_choose(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        class_name = self.text
        edit_second_screen.name = class_name
        edit_first_screen.active = False
        edit_second_screen.active = True
        con = db.create_connection('file.db')
        class_id = db.selectvalue(con, 'classid', 'class_details', 'name', edit_second_screen.name)
        edit_second_screen.classid = class_id[0][0]
        con.close()


# Takes you to the edit class details screen
class class_dets_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        edit_second_screen.active = False
        edit_class_dets_screen.active = True
        con = db.create_connection('file.db')
        data = db.select_all_value(con, 'class_details', 'name', edit_second_screen.name)
        con.close()


# puts all members in the class whether they are gymnast or coaches on the screen with a remove button
class edit_class_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        edit_class_screen.buttons = [edit_class_screen.close_button, edit_class_screen.back_button,
                                     edit_class_screen.submit]
        edit_second_screen.active = False
        edit_class_screen.active = True
        ids = []
        con = db.create_connection('file.db')
        ids_raw = db.selectvalue(con, 'memberid', 'class', 'classid', edit_second_screen.classid)
        for i in ids_raw:
            for j in i:
                ids.append(j)
        details = []

        for i in ids:
            data = db.select_all_value(con, 'members', 'id', i)
            try:
                details.append(data[0])
            except:
                pass
        con.close()
        gymnasts = []
        coaches = []
        for i in details:
            if i[4] == 'gymnast':
                gymnasts.append(i)
            else:
                coaches.append(i)
        count = 1
        font = pg.font.Font('freesansbold.ttf', 16)
        for i in coaches:
            remove = remove_member_from_class((SCR_W * 2 / 3), (SCR_H * (count / (SCR_H // 30))), 50, 25, 'Remove',
                                              True)
            edit_class_screen.buttons.append(remove)
            stri = i[2] + ' ' + i[3]
            text = font.render(stri, True, WHITE)
            text_to_screen = [text, (SCR_W * (1 / 3), (SCR_H * (count / (SCR_H // 30))))]
            edit_class_screen.text.append(text_to_screen)
            edit_class_screen.links.append([i[0], remove])

            count += 1
        for i in gymnasts:
            remove = remove_member_from_class((SCR_W * 2 / 3), (SCR_H * (count / (SCR_H // 30))), 50, 25, 'Remove',
                                              True)
            edit_class_screen.buttons.append(remove)
            stri = i[2] + ' ' + i[3]
            text = font.render(stri, True, WHITE)
            text_to_screen = [text, (SCR_W * (1 / 3), (SCR_H * (count / (SCR_H // 30))))]
            edit_class_screen.text.append(text_to_screen)
            edit_class_screen.links.append([i[0], remove])

            count += 1


# if pressed once, turns red, twice, turn back agiain.
class remove_member_from_class(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        if self.colour == RED:
            self.colour = COLOUR_ACTIVE
        else:
            self.colour = RED


# Takes all users in the class with the remove button linked to them red and deletes them from the class
class remove_submit(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        con = db.create_connection('file.db')
        for i in edit_class_screen.links:
            if i[1].colour == RED:
                db.delete(con, 'class', 'memberid', 'classid', (i[0], edit_second_screen.classid))

        edit_class_screen.active = False
        admin_base_page.active = True
        edit_class_screen.text = []
        data = db.select_all_value(con, 'class_details', 'name', edit_second_screen.name)
        data = data[0]
        num_kids = data[4]
        # decreases the number in the class by 1
        num_kids -= 1
        db.update(con, 'class_details', 'kidsInClass', 'classid', (num_kids, data[0]))
        con.close()


# allows you to edit the days and times the class runs
class edit_class_dets_next(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        for i in edit_class_dets_screen.input_boxes:

            if i.show == True:
                i.show = False

        no_days = int(edit_class_dets_screen.input_boxes[1].text)
        for i in range(1, no_days + 1):
            day = InputBox((SCR_W / 4) - 100, (SCR_H * (i / 8)), 100, 30, 'enter day', True)
            time = InputBox((SCR_W * (3 / 4)) - 100, (SCR_H * (i / 8)), 100, 30, 'enter time', True)
            edit_class_dets_screen.input_boxes.append(day)
            edit_class_dets_screen.input_boxes.append(time)
        edit_class_dets_screen.next.active = False
        edit_class_dets_screen.submit.active = True


# takes the updates and submits them into the database
class ed_class_dets_submit(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):

        day_time = ''
        for i in range(3, 3 + (len(edit_class_dets_screen.input_boxes) - 3), 2):
            day = edit_class_dets_screen.input_boxes[i].text
            time = edit_class_dets_screen.input_boxes[(i + 1)].text
            day_time += day + '/' + time + ','
        con = db.create_connection('file.db')
        db.update(con, 'class_details', 'no_days', 'classid',
                  (edit_class_dets_screen.input_boxes[1].text, edit_second_screen.classid))
        db.update(con, 'class_details', 'name', 'classid',
                  (edit_class_dets_screen.input_boxes[0].text, edit_second_screen.classid))
        db.update(con, 'class_details', 'MaxKidsInClass', 'classid',
                  (edit_class_dets_screen.input_boxes[2].text, edit_second_screen.classid))
        db.update(con, 'class_details', 'days_times', 'classid',
                  (day_time, edit_second_screen.classid))
        to_remove = []
        con.close()
        for i in edit_class_dets_screen.input_boxes:
            i.text = i.ori_text
            i.txt_surface = FONT.render(i.text, True, i.colour)
            if i.show == True:
                i.show = False
                to_remove.append(i)
            elif i.show == False:
                i.show = True

        for i in to_remove:
            edit_class_dets_screen.input_boxes.remove(i)

        # reset
        admin_base_page.active = True
        edit_class_dets_screen.active = False


# takes you to the set pay screen
class pay_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        admin_base_page.active = False
        pay_screen.active = True


# inserts pay into the database
class pay_submit(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        id = pay_screen.input_boxes[0].text
        pay = pay_screen.input_boxes[1].text
        con = db.create_connection('file.db')
        db.perform_command(con, '''INSERT INTO payrate VALUES(?,?)''', (int(id), float(pay)))
        con.close()
        pay_screen.active = False
        admin_base_page.active = True
        for i in pay_screen.input_boxes:
            i.text = i.ori_text
            i.txt_surface = FONT.render(i.text, True, i.colour)


# takes user to badges screen
class badges_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        admin_base_page.active = False
        badge_screen.active = True


# updates members table of specified id number with added badges
class badges_submit(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        id = badge_screen.input_boxes[0].text
        badge = badge_screen.input_boxes[1].text
        con = db.create_connection('file.db')
        value = db.selectvalue(con, 'badges', 'members', 'id', id)
        value = value[0][0]
        string_add = '{} {},'.format(value, badge)
        db.update(con, 'members', 'badges', 'id', (string_add, id))
        con.close()
        badge_screen.active = False
        admin_base_page.active = True
        for i in badge_screen.input_boxes:
            i.text = i.ori_text
            i.txt_surface = FONT.render(i.text, True, i.colour)


# gymnast buttons

# prints all member details onto the member details screen
class member_details_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    # continue
    def pressed_func(self):
        gymnast.active = False
        member_details_screen.active = True
        id = gymnast.memberid
        con = db.create_connection('file.db')
        details = db.select_all_value(con, 'members', 'id', id)
        details = details[0]
        con.close()
        welcome_string = 'Welcome {} {}'.format(details[2], details[3])
        welcome_text = font.render(welcome_string, True, WHITE)
        text_to_screen_1 = [welcome_text, (SCR_W * (1 / 8), (SCR_H * 1 / 16))]
        member_details_screen.text.append(text_to_screen_1)
        id_text = 'ID number: {}'.format(details[0])
        member_text = 'Member Type: {}'.format(details[4])
        dob_text = 'DOB: {}'.format(details[5])
        joined_text = 'Date joined: {}'.format(details[6])
        number_text = 'Phone Number: {}'.format(details[7])
        medical_text = 'Medical Information: {}'.format(details[8])
        postcode_text = 'Postcode: {}'.format(details[9])
        id_text = font.render(id_text, True, WHITE)
        member_text = font.render(member_text, True, WHITE)
        dob_text = font.render(dob_text, True, WHITE)
        joined_text = font.render(joined_text, True, WHITE)
        number_text = font.render(number_text, True, WHITE)
        medical_text = font.render(medical_text, True, WHITE)
        postcode_text = font.render(postcode_text, True, WHITE)

        text_to_screen_2 = [id_text, (SCR_W * (3 / 8), (SCR_H * 1 / 8))]
        text_to_screen_3 = [member_text, (SCR_W * (3 / 8), (SCR_H * 2 / 8))]
        text_to_screen_4 = [dob_text, (SCR_W * (3 / 8), (SCR_H * 3 / 8))]
        text_to_screen_5 = [joined_text, (SCR_W * (3 / 8), (SCR_H * 4 / 8))]
        text_to_screen_6 = [number_text, (SCR_W * (3 / 8), (SCR_H * 5 / 8))]
        text_to_screen_7 = [medical_text, (SCR_W * (3 / 8), (SCR_H * 6 / 8))]
        text_to_screen_8 = [postcode_text, (SCR_W * (3 / 8), (SCR_H * 7 / 8))]
        member_details_screen.text.append(text_to_screen_2)
        member_details_screen.text.append(text_to_screen_3)
        member_details_screen.text.append(text_to_screen_4)
        member_details_screen.text.append(text_to_screen_5)
        member_details_screen.text.append(text_to_screen_6)
        member_details_screen.text.append(text_to_screen_7)
        member_details_screen.text.append(text_to_screen_8)


# takes user to a page in which they can view their class name, coaches, badges and can press the console chat button
class gymnast_general_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        gymnast.active = False
        gymnast_general_screen.active = True
        con = db.create_connection('file.db')
        data = db.selectvalue(con, 'classid', 'class', 'memberid', gymnast.memberid)
        data = data[0]
        data = data[0]
        dets = db.select_all_value(con, 'class_details', 'classid', data)
        dets = dets[0]
        name = dets[1]
        coaches = []
        all_in_class = db.selectvalue(con, 'memberid', 'class', 'classid', dets[0])
        for i in all_in_class:
            members = db.select_all_value(con, 'members', 'id', i[0])
            for i in members:
                if i[4] == 'coach':
                    coaches.append(i)

                if str(i[0]) == str(gymnast.memberid):
                    badges = i[11]

        try:
            all_badges = badges.split(',')
            for i in range(len(all_badges)):
                try:
                    badges = font.render(all_badges[i], True, WHITE)
                    badges = [badges, (SCR_W * (4 / 8), (SCR_H * (4 + i) / 16))]
                    gymnast_general_screen.text.append(badges)
                except:
                    pass
        except:
            pass
        con.close()

        class_name = 'Class: {}'.format(name)
        class_name_text = font.render(class_name, True, WHITE)
        text_to_screen_1 = [class_name_text, (SCR_W * (1 / 8), (SCR_H * 1 / 16))]
        gymnast_general_screen.text.append(text_to_screen_1)
        coaches_title = 'Coaches:'
        coaches_title = font.render(coaches_title, True, WHITE)
        coaches_title = [coaches_title, (SCR_W * (1 / 8), (SCR_H * 4 / 16))]
        gymnast_general_screen.text.append(coaches_title)
        calender_title = 'Class times:'
        calender_title = font.render(calender_title, True, WHITE)
        calender_title = [calender_title, (SCR_W * (1 / 8), (SCR_H * 2 / 16))]
        gymnast_general_screen.text.append(calender_title)
        badges_title = 'Badges:'
        badges_title = font.render(badges_title, True, WHITE)
        badges_title = [badges_title, (SCR_W * (4 / 8), (SCR_H * 4 / 16))]
        gymnast_general_screen.text.append(badges_title)

        for i in range(len(coaches)):
            text = '{} {}'.format(coaches[i][2], coaches[i][3])
            text = font.render(text, True, WHITE)
            text = [text, (SCR_W * (1 / 8), (SCR_H * ((i + 5) / 16)))]
            gymnast_general_screen.text.append(text)


# runs the game as an external system
class game_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        os.system('python game.py')


# gymnast and coach
# connects to server.py to chat to others
class console_chat_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        chat = True
        client_socket = socket.socket()
        port = 12345
        client_socket.connect(('127.0.0.1', port))
        con = db.create_connection('file.db')
        if gymnast_general_screen.active == True:
            details = db.select_all_value(con, 'members', 'id', gymnast.memberid)
        elif coach_base_page.active == True:
            details = db.select_all_value(con, 'members', 'id', coach_base_page.memberid)
        details = details[0]
        con.close()
        client_socket.send(pickle.dumps('{} {}'.format(details[2], details[3])))
        recv_msg = client_socket.recv(1024)
        print(pickle.loads(recv_msg))
        data = []

        def get_input():
            data.append(input('enter: '))

        while chat:
            # allows input to be asked for and searching for incoming messages at the same time
            input_thread = threading.Thread(target=get_input)
            input_thread.start()
            input_thread.join()
            if data[0] == 'exit':
                client_socket.send(pickle.dumps('{} {} has left'.format(details[2],details[3])))
                break
            else:
                client_socket.send(pickle.dumps(data[0]))
                data.pop(0)
            print(pickle.loads(client_socket.recv(1024)))




        client_socket.close()


# coach only button
# allows coach to view hourly pay, weekly pay and monthly pay
class timesheet_but(Button):
    def __init__(self, x, y, w, h, text='', active=False, colour=COLOUR_ACTIVE):
        super().__init__(x, y, w, h, text, active, colour)

    def pressed_func(self):
        coach_base_page.active = False
        days = []
        for i in coach_base_page.days:
            for j in i:
                temp = j.split(',')
                days.append(temp)
        just_times = []
        for i in days:
            for j in i:
                if j != '':
                    time = j.split('/')

                    just_times.append(time[1])
        total_hours = 0
        new_times = []
        for i in range(len(just_times)):
            new_times.append(just_times[i].replace(':', '.'))
        for i in new_times:
            a, b = i.split('-')
            c = float(b) - float(a)
            hours = c % 12
            total_hours += hours
        hours_text = font.render('Hours Worked per week: {:.2f}'.format(total_hours), True, WHITE)
        hours_text = [hours_text, (SCR_W * (2 / 8), (SCR_H * 1 / 6))]
        timesheet_screen.text.append(hours_text)
        con = db.create_connection('file.db')
        data = db.selectvalue(con, 'pay', 'payrate', 'id', coach_base_page.memberid)
        rate = data[0][0]
        con.close()
        rate_text = font.render('Rate of pay: {:.2f}'.format(rate), True, WHITE)
        rate_text = [rate_text, (SCR_W * (2 / 8), (SCR_H * 2 / 6))]
        timesheet_screen.text.append(rate_text)
        money_week = font.render('Money per week: £{:.2f}'.format(total_hours * rate), True, WHITE)
        money_week = [money_week, (SCR_W * (2 / 8), (SCR_H * 3 / 6))]
        timesheet_screen.text.append(money_week)
        money_month = font.render('Money per month: £{:.2f}'.format(total_hours * rate * 4.345), True, WHITE)
        money_month = [money_month, (SCR_W * (2 / 8), (SCR_H * 4 / 6))]
        timesheet_screen.text.append(money_month)
        timesheet_screen.active = True


# Text box class
class InputBox:

    def __init__(self, x, y, w, h, text='', show=False, view_text=True):
        self.rect = pg.Rect(x, y, w, h)
        self.colour = WHITE  # COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.colour)
        self.active = False
        self.show = show
        self.output = None
        self.entered = False
        self.view_text = view_text
        self.ori_text = text

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                self.text = ''
            else:
                self.active = False
            # Change the current color of the input box.
            self.colour = COLOUR_ACTIVE if self.active else WHITE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                    self.entered = False
                # Re-render the text.
                length = len(self.text)
                star = '*' * length
                if self.view_text:
                    self.txt_surface = FONT.render(self.text, True, self.colour)
                else:
                    self.txt_surface = FONT.render(star, True, self.colour)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(screen, self.colour, self.rect, 2)


# main class screen

class screen:

    def __init__(self, active=False):
        self.active = active
        self.previous = None
        self.background_colour = BACKGROUND_COLOUR
        self.buttons = []
        self.input_boxes = []
        self.text = []
    # runs the screen checking if button  or input boxes are clicked on
    def screen_run(self):
        for event in pg.event.get():
            for i in range(len(self.buttons)):
                self.buttons[i].button_handle((event))
            for box in self.input_boxes:
                if box.show == True:
                    box.handle_event(event)

        for box in self.input_boxes:
            box.update()

        SCREEN.blit(b, (0, 0))
        for box in self.input_boxes:
            if box.show == True:
                box.draw(SCREEN)
        for button in self.buttons:
            if button.active == True:
                button.draw()
        for t in self.text:
            SCREEN.blit(t[0], t[1])
        pg.display.update()


## login screen class
class login(screen):

    def __init__(self, active):
        super().__init__(active)
        self.user_text = InputBox((SCR_W / 2) - 100, (SCR_H / 2) - 50, 100, 30, 'enter memberID', True)
        self.password_text = InputBox((SCR_W / 2) - 100, (SCR_H / 2), 100, 30, 'enter password', True, False)
        self.input_boxes = [self.user_text, self.password_text]
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.submit_login_button = Submit_Button((SCR_W / 2) - 50, (SCR_H / 2) + 50, 50, 30, 'SUBMIT', True)
        self.new_member_button = New_Member_Button(0, 0, 50, 30, 'New Member?', True)
        self.buttons = [self.close_button, self.submit_login_button, self.new_member_button]
        con = db.create_connection('file.db')
        con.close()


## New member screen 1
class new_member_pass(screen):

    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.memberID = InputBox((SCR_W / 2) - 100, (SCR_H / 2) - 25, 100, 30, 'Enter your memberID', True)
        self.submit_button = New_Member_Button_submit((SCR_W / 2) - 50, (SCR_H / 2) + 50, 50, 30, 'SUBMIT', True)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.submit_button, self.back_button]
        self.input_boxes = [self.memberID]


## New member screen 2
class new_member_pass2(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.password1 = InputBox((SCR_W / 2) - 100, (SCR_H / 2) - 50, 100, 30, 'enter new password', True, False)
        self.password2 = InputBox((SCR_W / 2) - 100, (SCR_H / 2), 100, 30, 're-enter password  ', True, False)
        self.submit_button = New_Member_Button_submit2((SCR_W / 2) - 50, (SCR_H / 2) + 50, 50, 30, 'SUBMIT', True)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.submit_button, self.back_button]
        self.input_boxes = [self.password1, self.password2]
        self.font = pg.font.Font('freesansbold.ttf', 16)
        self.pass_text_help = self.font.render(
            'Your password must be at least 8 characters long, have at least 1 capital letter, have at least 1 special character and have at least 1 digit ',
            True, WHITE)
        self.pass_text_help_to_screen = [self.pass_text_help,
                                         ((SCR_W * (1 / 2)) - (self.pass_text_help.get_width() / 2), SCR_H * (1 / 8))]
        self.text = [self.pass_text_help_to_screen]


## Class for admin page
class admin_base(screen):

    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.create_member = add_member(SCR_W * 1 / 5 - 50, SCR_H * 1 / 3 - 50, 100, 100, ' create member ', True)
        self.create_class = add_class_but(SCR_W * 2 / 5 - 50, SCR_H * 1 / 3 - 50, 100, 100, '  Create class  ', True)
        self.add_to_class = add_to_class_but(SCR_W * 3 / 5 - 50, SCR_H * 1 / 3 - 50, 100, 100, '  Add to class  ', True)
        self.badges = badges_but(SCR_W * 4 / 5 - 50, SCR_H * 1 / 3 - 50, 100, 100, ' Add badge ', True)
        self.classes = classes_but(SCR_W * 1 / 5 - 50, SCR_H * 2 / 3 - 50, 100, 100, ' Take Register ', True)
        self.pay = pay_but(SCR_W * 2 / 5 - 50, SCR_H * 2 / 3 - 50, 100, 100, 'Set employee pay', True)
        self.edit = edit_but(SCR_W * 3 / 5 - 50, SCR_H * 2 / 3 - 50, 100, 100, '      Edit      ', True)
        self.view_reg = view_register(SCR_W * 4 / 5 - 50, SCR_H * 2 / 3 - 50, 100, 100, ' View Register ', True)

        self.buttons = [self.close_button, self.back_button, self.create_member, self.create_class, self.add_to_class,
                        self.classes, self.pay, self.edit, self.view_reg, self.badges]
        self.text = []


class create_member(screen):

    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.submit = add_member_submit((SCR_W / 2) - 50, (SCR_H * (11 / 12)), 50, 30, 'Submit', False)
        self.next = add_member_next((SCR_W / 2) - 50, (SCR_H * (11 / 12)), 50, 30, 'Next', True)
        self.buttons = [self.close_button, self.back_button, self.submit, self.next]
        self.firstname = InputBox((SCR_W / 2) - 100, (SCR_H * (1 / 12)), 100, 30, 'enter firstname', True)
        self.lastname = InputBox((SCR_W / 2) - 100, (SCR_H * (3 / 12)), 100, 30, 'enter lastname', True)
        self.type = InputBox((SCR_W / 2) - 100, (SCR_H * (5 / 12)), 100, 30, 'admin/coach/gymnast', True)
        self.DOB = InputBox((SCR_W / 2) - 100, (SCR_H * (7 / 12)), 100, 30, 'enter DOB', True)
        self.date_joined = InputBox((SCR_W / 2) - 100, (SCR_H * (9 / 12)), 100, 30, 'enter date_joined', True)
        self.mobile_number = InputBox((SCR_W / 2) - 100, (SCR_H * (1 / 12)), 100, 30, 'enter mobile number', False)
        self.medical = InputBox((SCR_W / 2) - 100, (SCR_H * (3 / 12)), 100, 30, 'enter medical information', False)
        self.postcode = InputBox((SCR_W / 2) - 100, (SCR_H * (5 / 12)), 100, 30, 'enter postcode', False)
        self.gender = InputBox((SCR_W / 2) - 100, (SCR_H * (7 / 12)), 100, 30, 'enter gender', False)
        self.input_boxes = [self.firstname, self.lastname, self.type, self.DOB, self.date_joined, self.mobile_number,
                            self.medical, self.postcode, self.gender]


class create_class(screen):

    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.submit = add_class_submit((SCR_W / 2) - 50, (SCR_H * (11 / 12)), 50, 30, 'Submit', False)
        self.next = add_class_next((SCR_W / 2) - 50, (SCR_H * (11 / 12)), 50, 30, 'Next', True)
        self.buttons = [self.close_button, self.back_button, self.submit, self.next]
        self.name = InputBox((SCR_W / 2) - 100, (SCR_H * (1 / 12)), 100, 30, 'enter name of class', True)
        self.no_days = InputBox((SCR_W / 2) - 100, (SCR_H * (5 / 12)), 100, 30,
                                'enter number of days of class per week', True)
        self.kidsinClass = InputBox((SCR_W / 2) - 100, (SCR_H * (9 / 12)), 100, 30, 'enter max kids in class', True)
        self.input_boxes = [self.name, self.no_days, self.kidsinClass]


class add_to_class(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.next = add_to_class_id_next((SCR_W / 2) - 50, (SCR_H / 2) + 50, 50, 30, 'NEXT', True)
        self.buttons = [self.close_button, self.back_button, self.next]
        self.id_search = InputBox((SCR_W / 2) - 100, (SCR_H / 2) - 25, 100, 30, 'Enter memberID to add', True)
        self.input_boxes = [self.id_search]
        self.class_id = []
        self.classes = []

# set pay screen
class pay(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.submit = pay_submit((SCR_W / 2) - 50, (SCR_H / 2) + 75, 50, 30, 'NEXT', True)
        self.buttons = [self.close_button, self.back_button, self.submit]
        self.id = InputBox((SCR_W / 2) - 100, (SCR_H / 2) - 25, 100, 30, 'Enter memberID to set pay for', True)
        self.pay_input = InputBox((SCR_W / 2) - 100, (SCR_H / 2) + 25, 100, 30, 'Enter rate of pay for employee', True)
        self.input_boxes = [self.id, self.pay_input]

# add badges screen
class badges(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.submit = badges_submit((SCR_W / 2) - 50, (SCR_H / 2) + 75, 50, 30, 'SUBMIT', True)
        self.buttons = [self.close_button, self.back_button, self.submit]
        self.id = InputBox((SCR_W / 2) - 100, (SCR_H / 2) - 25, 100, 30, 'Enter memberID to add badge to', True)
        self.badges_input = InputBox((SCR_W / 2) - 100, (SCR_H / 2) + 25, 100, 30, 'Enter name of badge', True)
        self.input_boxes = [self.id, self.badges_input]

# screen to show all classes
class classes(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.back_button]
        self.input_boxes = []
        self.classes = []
        self.next_screen = []

class all_members(screen):
    def __init__(self,active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.back_button]
        self.members = []


class Register_main(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.back_button]
        self.input_boxes = []


class Regster_class(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.submit_button = register_submit((SCR_W * 6 / 8), SCR_H - 100, 50, 30, 'SUBMIT', True)
        self.buttons = [self.close_button, self.back_button, self.submit_button]
        self.input_boxes = []
        self.classid = ''
        self.text = []
        self.links = []
        self.day = []
        self.class_name = ''


class reg_view_1(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.back_button]
        self.input_boxes = []
        self.classid = ''
        self.classes = []


class reg_view_2(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.back_button]
        self.input_boxes = []
        self.day = ''
        self.classid = ''
        self.classes = []
        self.text = []


class edit_first(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.back_button]

        self.classes = []


class edit_second(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.button1 = class_dets_but(SCR_W * 1 / 3, SCR_H * 1 / 2, 50, 30, 'Edit class details', True)
        self.button2 = edit_class_but(SCR_W * 2 / 3, SCR_H * 1 / 2, 50, 30, 'Edit class', True)
        self.buttons = [self.close_button, self.back_button, self.button1, self.button2]
        self.name = ''
        self.classid = ''


class edit_class_dets(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.next = edit_class_dets_next((SCR_W / 2) - 50, (SCR_H * (11 / 12)), 50, 30, 'next', True)
        self.submit = ed_class_dets_submit((SCR_W / 2) - 50, (SCR_H * (11 / 12)), 50, 30, 'Submit', False)
        self.buttons = [self.close_button, self.back_button, self.submit, self.next]
        self.name = InputBox((SCR_W / 2) - 100, (SCR_H * (1 / 12)), 100, 30, 'enter name of class', True)
        self.no_days = InputBox((SCR_W / 2) - 100, (SCR_H * (5 / 12)), 100, 30,
                                'enter number of days of class per week', True)
        self.kidsinClass = InputBox((SCR_W / 2) - 100, (SCR_H * (9 / 12)), 100, 30, 'enter max kids in class', True)
        self.input_boxes = [self.name, self.no_days, self.kidsinClass]


class edit_class(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.submit = remove_submit((SCR_W * 6 / 8), SCR_H - 100, 50, 30, 'SUBMIT', True)
        self.buttons = [self.close_button, self.back_button, self.submit]
        self.text = []
        self.links = []


class chat(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.back_button]
        text = font.render('Chatroom in console', True, WHITE)
        text = [text, (SCR_W / 2, SCR_H / 2)]
        self.text = [text]


class gymnast_base(screen):

    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.details = member_details_but(SCR_W * 1 / 3, SCR_H * 1 / 4, 100, 100, 'member details', True)
        self.general = gymnast_general_but(SCR_W * 2 / 3, SCR_H * 1 / 4, 100, 100, ' General ', True)
        self.game_but = game_but(SCR_W * 1 / 2, SCR_H * 3 / 4, 100, 100, '    Game    ', True)
        self.buttons = [self.close_button, self.back_button, self.details, self.general, self.game_but]
        self.input_boxes = []
        self.memberid = ''


class member_details(screen):

    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.back_button]
        self.input_boxes = []
        self.text = []


class gymnast_general(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.console_chat = console_chat_but(SCR_W * 4 / 5, SCR_H * 7 / 8, 100, 100, 'Console chat', True)
        self.buttons = [self.close_button, self.back_button, self.console_chat]
        self.text = []
        self.days = []


class coaches_base(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.register = classes_but(SCR_W * 2 / 5 - 50, SCR_H * 7 / 8 - 50, 100, 100, 'Take Register', True)
        self.timesheet = timesheet_but(SCR_W * 1 / 5 - 50, SCR_H * 7 / 8 - 50, 100, 100, 'Timesheet', True)
        self.console = console_chat_but(SCR_W * 3 / 5 - 50, SCR_H * 7 / 8 - 50, 100, 100, 'Console chat', True)
        self.view_reg = view_register(SCR_W * 4 / 5 - 50, SCR_H * 7 / 8 - 50, 100, 100, 'View Register', True)
        self.buttons = [self.close_button, self.back_button, self.register, self.timesheet, self.console, self.view_reg]
        self.text = []
        self.memberid = ''
        self.days = []
        calender_title = 'Class times:'
        calender_title = font.render(calender_title, True, WHITE)
        calender_title = [calender_title, (SCR_W * (1 / 8), (SCR_H * 1 / 8))]
        self.text.append(calender_title)


class timesheet(screen):
    def __init__(self, active):
        super().__init__(active)
        self.close_button = Close_Button(SCR_W - 65, 0, 50, 30, 'QUIT', True, RED)
        self.back_button = Back_Button(0, 0, 50, 30, 'Back', True)
        self.buttons = [self.close_button, self.back_button]
        self.text = []

# class to work out timetable given an id number
def calender(id):
    con = db.create_connection('file.db')
    data = db.selectvalue(con, 'classid', 'class', 'memberid', id)
    times = []
    try:
        for i in data:
            new_data = i[0]
            times_add = db.selectvalue(con, 'days_times', 'class_details', 'classid', new_data)
            for i in times_add:
                times.append(i)
    except:
        pass
    con.close()
    return times





# set up all screen

login_page = login(True)
admin_base_page = admin_base(False)
gymnast = gymnast_base(False)
new_password = new_member_pass(False)
new_password1 = new_member_pass2(False)
create_member_screen = create_member(False)
add_to_class_screen = add_to_class(False)
create_class_screen = create_class(False)
classes_screen = classes(False)
register_screen = Register_main(False)
register_show_screen = Regster_class(False)
member_details_screen = member_details(False)
gymnast_general_screen = gymnast_general(False)
coach_base_page = coaches_base(False)
timesheet_screen = timesheet(False)
pay_screen = pay(False)
edit_first_screen = edit_first(False)
edit_second_screen = edit_second(False)
edit_class_dets_screen = edit_class_dets(False)
edit_class_screen = edit_class(False)
chat_screen = chat(False)
reg_view_1_screen = reg_view_1(False)
reg_view_2_screen = reg_view_2(False)
badge_screen = badges(False)
all_members_screen = all_members(False)

#set up back button relationships

back_relationships = {gymnast: login_page,
                      member_details_screen: gymnast,
                      new_password: login_page,
                      new_password1: new_password,
                      coach_base_page: login_page,
                      admin_base_page: login_page,
                      create_member_screen: admin_base_page,
                      add_to_class_screen: admin_base_page,
                      pay_screen: admin_base_page,
                      badge_screen: admin_base_page,
                      create_class_screen: admin_base_page,
                      classes_screen: admin_base_page,
                      register_screen: classes_screen,
                      register_show_screen: register_screen,
                      gymnast_general_screen: gymnast,
                      timesheet_screen: coach_base_page,
                      edit_first_screen: admin_base_page,
                      edit_second_screen: edit_first_screen,
                      edit_class_dets_screen: edit_second_screen,
                      edit_class_screen: edit_second_screen,
                      chat_screen: gymnast_general_screen,
                      reg_view_1_screen: admin_base_page,
                      reg_view_2_screen: reg_view_1_screen,
                      all_members_screen: edit_second_screen}

# main loop


while True:
    while login_page.active:
        login_page.screen_run()
    while new_password.active:
        new_password.screen_run()
    while new_password1.active:
        new_password1.screen_run()
    while gymnast.active:
        gymnast.screen_run()
    while member_details_screen.active:
        member_details_screen.screen_run()
    while gymnast_general_screen.active:
        gymnast_general_screen.screen_run()
    while admin_base_page.active:
        admin_base_page.screen_run()
    while create_member_screen.active:
        create_member_screen.screen_run()
    while create_class_screen.active:
        create_class_screen.screen_run()
    while add_to_class_screen.active:
        add_to_class_screen.screen_run()
    while classes_screen.active:
        classes_screen.screen_run()
    while register_screen.active:
        register_screen.screen_run()
    while register_show_screen.active:
        register_show_screen.screen_run()
    while coach_base_page.active:
        coach_base_page.screen_run()
    while timesheet_screen.active:
        timesheet_screen.screen_run()
    while pay_screen.active:
        pay_screen.screen_run()
    while edit_first_screen.active:
        edit_first_screen.screen_run()
    while edit_second_screen.active:
        edit_second_screen.screen_run()
    while edit_class_dets_screen.active:
        edit_class_dets_screen.screen_run()
    while edit_class_screen.active:
        edit_class_screen.screen_run()
    while chat_screen.active:
        chat_screen.screen_run()
    while reg_view_1_screen.active:
        reg_view_1_screen.screen_run()
    while reg_view_2_screen.active:
        reg_view_2_screen.screen_run()
    while badge_screen.active:
        badge_screen.screen_run()
    while all_members_screen.active:
        all_members_screen.screen_run()

    pg.display.update()
