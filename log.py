from sqlalchemy import select, create_engine, Table, Column, Integer, Float, String, func, and_, desc
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import IntegrityError
import sys
import os
import PySimpleGUI as sg

VERSION = 'V1.07'

Base = automap_base()

sg.theme('BlueMono')

class Config(Base):
    __tablename__ = 'config'

    def get_value(sql_session, domain, name):
        with sql_session.begin():
            config = sql_session.execute(select(Config)
                                         .where(and_(Config.domain == domain,
                                                     Config.name == name))).scalars().all()
            if len(config) > 0:
                for c in config:
                    value = c.value
            else:
                value = None

        return value

class Burial(Base):
    __tablename__ = 'burial'
    input_given_names = sg.Input(tooltip = 'Enter the given names for the record, eg Fredric William', key = '-given_names-', enable_events = True, focus = True)
    input_family_name = sg.Input(tooltip = 'Enter the family name for the record, eg Smith', key = '-family_name-', enable_events = True)
    button_date_of_birth = sg.CalendarButton('Date of Birth', auto_size_button = True, target = '-date_of_birth-', no_titlebar = False, tooltip = 'Enter date of birth if known', format = '%Y-%m-%d', title = 'Date of Birth')
    input_date_of_birth = sg.Input(key = '-date_of_birth-', readonly = True, size = (12, 1))
    button_date_of_death = sg.CalendarButton('Date of Death', auto_size_button = True, target = '-date_of_death-', no_titlebar = False, tooltip = 'Enter date of death, if only year is known select 1st January', format = '%Y-%m-%d', title = 'Burial Date')
    input_date_of_death = sg.Input(key = '-date_of_death-', readonly = True, size = (12, 1))
    button_date_of_burial = sg.CalendarButton('Burial Date', auto_size_button = True, target = '-date_of_burial-', no_titlebar = False, tooltip = 'Enter date of burial, if only year is known select 1st January', format = '%Y-%m-%d', title = 'Burial Date')
    input_date_of_burial = sg.Input(key = '-date_of_burial-', readonly = True, size = (12, 1))
    checkbox_ashes = sg.Checkbox('Ashes', tooltip = 'Click if ashes are being intered', key = '-ashes-')
#    checkbox_grave_full = sg.Checkbox('Grave Full', tooltip = 'Click if grave is full', key = '-grave_full-')
    text_age_years = sg.Text('Age Years', key = '#age_years#')
    input_age_years = sg.Input(tooltip = 'Enter an age in years', size = (6, 1), enable_events = True, key = '-age_years-')
    text_age_months = sg.Text('Age Months', key = '#age_months#')
    input_age_months = sg.Input(tooltip = 'Enter the age months, usually used for infants', size = (6, 1), enable_events = True, key = '-age_months-')
    text_age_days = sg.Text('Age Days', key = '#age_days#')
    input_age_days = sg.Input(tooltip = 'Enter the age days, usually used for infants', size = (6, 1), enable_events = True, key = '-age_days-')
    checkbox_stillborn = sg.Checkbox('Stillborn', tooltip = 'Click if stillborn, cannot be used if any of the age fields are set', enable_events = True, key = '-stillborn-')
    input_source_document_ref = sg.Input(tooltip = 'Enter the document reference number', size = (5, 1), enable_events = True, key = '-source_document_ref-')
    input_cross_reference = sg.Input(tooltip = 'Enter the cross reference to a previous entry', size = (5, 1), enable_events = True, key = '-cross_reference-')
    input_page_number = sg.Input(tooltip = 'Enter the document page number for the record', size = (4, 1), enable_events = True, key = '-page_number-')
    input_see_page_number = sg.Input(tooltip = 'Enter any page number cross reference', size = (25, 1), enable_events = True, key = '-see_page_number-')
    input_plot = sg.Input(tooltip = 'Enter the plot identification for the grave', size = (15, 1), key = '-plot-')
    input_plot_row = sg.Input(tooltip = 'Enter the plot row identification for the grave', size = (15, 1), key = '-plot_row-')
    input_plot_row_number = sg.Input(tooltip = 'Enter the plot row number of the grave', size = (15, 1), enable_events = True, key = '-plot_row_number-')
    multiline_notes = sg.Multiline(autoscroll = True, size = (50, 5), key = '-notes-', tooltip = 'Enter any notes or text that does not fit in other fields')
    spin_confidence_level = sg.Spin(('Low', 'Medium', 'High'), initial_value = 'High', size = (8, 1), key = '-confidence_level-', tooltip = 'Select a confidence level of the data entered')
    button_save = sg.Button('Save')
    records_entered = sg.Text('Records entered: 0', font = (None, 14))

    default_plot = None

    def set_default_plot(default_plot):
        Burial.default_plot = default_plot

    # Get the last non null plot to be entered
    def get_last_plot(sql_session):
        with sql_session.begin():
            records = sql_session.execute(select(Burial)
                                         .where(Burial.plot != None)
                                         .order_by(desc(Burial.id)).limit(1)).scalars().all()
            if len(records) > 0:
                value = records[0].plot
            else:
                value = None

        return value

    def gui_layout(source_document):
        return [[sg.Text(source_document, expand_x = True, justification = 'center', font = (None, 25))],
                [sg.Text('Given Names', size = (12, 1), text_color = 'red'), Burial.input_given_names],
                [sg.Text('Family Name', size = (12, 1), text_color = 'red'), Burial.input_family_name],
                [Burial.button_date_of_birth, Burial.input_date_of_birth],
                [Burial.button_date_of_death,
                 Burial.input_date_of_death,
                 Burial.button_date_of_burial,
                 Burial.input_date_of_burial,
                 Burial.checkbox_ashes],
#                 Burial.checkbox_grave_full],
                [Burial.text_age_years, Burial.input_age_years,
                 Burial.text_age_months, Burial.input_age_months,
                 Burial.text_age_days, Burial.input_age_days,
                 Burial.checkbox_stillborn],
                [sg.Text('Document reference'), Burial.input_source_document_ref,
                 sg.Text('Cross reference'), Burial.input_cross_reference],
                [sg.Text('Page number'), Burial.input_page_number,
                 sg.Text('See page number(s)'), Burial.input_see_page_number],
                [sg.Text('Plot'), Burial.input_plot, sg.Text('Row'), Burial.input_plot_row, sg.Text('Number'), Burial.input_plot_row_number],
                [sg.Text('Notes'), Burial.multiline_notes],
                [sg.Text('Data Entry Confidence'), Burial.spin_confidence_level],
                [sg.Button('Clear'), Burial.button_save, Burial.records_entered]]

    def gui_layout_new_record():
        Burial.input_given_names.set_focus()
        Burial.input_given_names.update(value = '')
        Burial.input_family_name.update(value = '')
        Burial.input_date_of_birth.update(value = '')
        Burial.input_date_of_death.update(value = '')
        Burial.input_date_of_burial.update(value = '')
        Burial.checkbox_ashes.update(value = False)
 #       Burial.checkbox_grave_full.update(value = False)
        Burial.text_age_years.update(text_color = 'black')
        Burial.input_age_years.update(value = '', disabled = False)
        Burial.text_age_months.update(text_color = 'black')
        Burial.input_age_months.update(value = '', disabled = False)
        Burial.text_age_days.update(text_color = 'black')
        Burial.input_age_days.update(value = '', disabled = False)
        Burial.checkbox_stillborn.update(value = False, disabled = False)
        Burial.input_see_page_number.update(value = '')
        Burial.input_cross_reference.update(value = '')
        Burial.input_plot.update(value = '')
        Burial.input_plot_row.update(value = '')
        Burial.input_plot_row_number.update(value = '')
        Burial.multiline_notes.update(value = '')
        Burial.spin_confidence_level.update(value = 'High')
        Burial.button_save.update(disabled = True)

        with sql_session.begin():
            row_count = sql_session.query(Burial).count()
        Burial.records_entered.update(value = 'Records entered: ' + str(row_count))
        if row_count == 0:
            Burial.button_date_of_birth.calendar_default_date_M_D_Y = (1, None, 1900)
            Burial.button_date_of_death.calendar_default_date_M_D_Y = (1, None, 1900)
            Burial.button_date_of_burial.calendar_default_date_M_D_Y = (1, None, 1900)
            Burial.input_source_document_ref.update(value = '')
            Burial.input_page_number.update(value = '')
        else:
            stmt = select(func.min(Column('date_of_birth', String)).label('date_of_birth'),
                          func.max(Column('date_of_death', String)).label('date_of_death'),
                          func.max(Column('date_of_burial', String)).label('date_of_burial'),
                          func.max(Column('source_document_ref', Integer)).label('source_document_ref'),
                          func.max(Column('page_number', Integer)).label('page_number')).select_from(Burial)
            with sql_session.begin():
                result = sql_session.execute(stmt)
                for r in result:
                    if r['date_of_birth']:
                        date_bits = r['date_of_birth'].split('-')
                        Burial.button_date_of_birth.calendar_default_date_M_D_Y = (int(date_bits[1]), None, int(date_bits[0]))
                    else:
                        Burial.button_date_of_birth.calendar_default_date_M_D_Y = (1, None, 1900)
                        Burial.input_date_of_birth.update(value = '')
                    if r['date_of_death']:
                        date_bits = r['date_of_death'].split('-')
                        Burial.button_date_of_death.calendar_default_date_M_D_Y = (int(date_bits[1]), None, int(date_bits[0]))
                    else:
                        Burial.button_date_of_death.calendar_default_date_M_D_Y = (1, None, 1900)
                        Burial.input_date_of_death.update(value = '')
                    if r['date_of_burial']:
                        date_bits = r['date_of_burial'].split('-')
                        Burial.button_date_of_burial.calendar_default_date_M_D_Y = (int(date_bits[1]), None, int(date_bits[0]))
                    else:
                        Burial.button_date_of_burial.calendar_default_date_M_D_Y = (1, None, 1900)
                        Burial.input_date_of_burial.update(value = '')
                    if r['source_document_ref']:
                        Burial.input_source_document_ref.update(value = str(int(r['source_document_ref']) + 1))
                    else:
                        Burial.input_source_document_ref.update(value = '')
                    if r['page_number']:
                        Burial.input_page_number.update(value = r['page_number'])
                    else:
                        Burial.input_page_number.update(value = '')
        if Burial.default_plot is None:
            Burial.input_plot.update(value = '')
        else:
            Burial.input_plot.update(value = Burial.default_plot)

    def save(values):
        burial = Burial()
        if values['-given_names-'].rstrip() == '':
            burial.given_names = None
        else:
            burial.given_names = values['-given_names-'].rstrip()
        if values['-family_name-'].rstrip() == '':
            burial.family_name = None
        else:
            burial.family_name = values['-family_name-'].rstrip()
        if values['-date_of_birth-'] == '':
            burial.date_of_birth = None
        else:
            burial.date_of_birth = values['-date_of_birth-']
        if values['-date_of_death-'] == '':
            burial.date_of_death = None
        else:
            burial.date_of_death = values['-date_of_death-']
        if values['-date_of_burial-'] == '':
            burial.date_of_burial = None
        else:
            burial.date_of_burial = values['-date_of_burial-']
        if values['-ashes-']:
            burial.ashes = True
        else:
            burial.ashes = False
#        if values['-grave_full-']:
#            burial.grave_full = True
#        else:
#            burial.grave_full = False
        if values['-age_years-'] == '':
            burial.age_years = None
        else:
            burial.age_years = int(values['-age_years-'])
        if values['-age_months-'] == '':
            burial.age_months = None
        else:
            burial.age_months = int(values['-age_months-'])
        if values['-age_days-'] == '':
            burial.age_days = None
        else:
            burial.age_days = int(values['-age_days-'])
        if values['-source_document_ref-'] == '':
            burial.source_document_ref = None
        else:
            burial.source_document_ref = values['-source_document_ref-'].rstrip()
        if values['-stillborn-']:
            burial.stillborn = True
        else:
            burial.stillborn = False
        if values['-cross_reference-'] == '':
            burial.cross_reference = None
        else:
            burial.cross_reference = values['-cross_reference-'].rstrip()
        if values['-page_number-'] == '':
            burial.page_number = None
        else:
            burial.page_number = values['-page_number-']
        if values['-see_page_number-'] == '':
            burial.see_page_number = None
        else:
            burial.see_page_number = values['-see_page_number-']
        if values['-plot-'] == '':
            burial.plot = None
        else:
            burial.plot = values['-plot-'].rstrip()
        if values['-plot_row-'] == '':
            burial.plot_row = None
        else:
            burial.plot_row = values['-plot_row-'].rstrip()
        if values['-plot_row_number-'] == '':
            burial.plot_row_number = None
        else:
            burial.plot_row_number = values['-plot_row_number-'].rstrip()
        if values['-notes-'] == '':
            burial.notes = None
        else:
            burial.notes = values['-notes-'].rstrip()
        if values['-confidence_level-'] in ('High', 'Medium', 'Low'):
            if values['-confidence_level-'] == 'High':
                burial.confidence_level = 3
            elif values['-confidence_level-'] == 'Medium':
                burial.confidence_level = 2
            else:
                burial.confidence_level = 1
        else:
            burial.confidence_level = 0

        try:
            with sql_session.begin():
                sql_session.add(burial)
                Burial.default_plot = burial.plot
        except IntegrityError as e:
            if str(e.orig).startswith('UNIQUE constraint failed'):
                m = str(e.orig).split(':')
                if m[1] == ' burial.source_document_ref':
                    sg.popup('The source document ref should be unique or empty')
                else:
                    sg.popup(e.orig, 'The data could not be saved because of the above error')
            else:
                sg.popup(e.orig, 'The data could not be saved because of the above error')
        except:
            e = sys.exc_info()[0]
            sg.popup_error(e, 'Please report this error to the software developer')
        else:
            Burial.gui_layout_new_record()

if __name__ == '__main__':
    def create_db(sql_session):
        with sql_session.begin():
            sql_session.execute('''create table burial (
                                   id integer primary key,
                                   given_names varchar(256) not null,
                                   family_name varchar(256) not null,
                                   date_of_birth varchar(32),
                                   date_of_death varchar(32),
                                   date_of_burial varchar(32),
                                   ashes integer,
                                   age_years integer,
                                   age_months integer,
                                   age_days integer,
                                   stillborn integer,
                                   source_document_ref integer unique,
                                   cross_reference integer,
                                   page_number integer,
                                   see_page_number varchar(256),
                                   plot varchar(32),
                                   plot_row varchar(32),
                                   plot_row_number varchar(32),
                                   notes text,
                                   confidence_level integer
                                   )''')
            sql_session.execute('''create table config (
                                   id integer primary key,
                                   domain varchar(256) not null,
                                   name varchar(256) not null,
                                   value varchar(256)
                                   )''')

    def add_created_by(sql_session):
        with sql_session.begin():
            config = Config()
            config.domain = 'Database'
            config.name = 'CreatedBy'
            config.value = 'log.py ' + VERSION
            sql_session.add(config)
            config = Config()
            config.domain = 'Database'
            config.name = 'Version'
            config.value = VERSION
            sql_session.add(config)

    def get_config_value(sql_session, domain, name):
        return Config.get_value(sql_session, domain, name)

    def get_source_document(sql_session):
        return get_config_value(sql_session, 'Source', 'DocumentName')

    def create_source_document(sql_session):
        source_doc = sg.popup_get_text('Enter the source document name')
        if source_doc is None or source_doc.rstrip() == '':
            sg.popup('A source document name is required before data can be entered')
            exit()
        with sql_session.begin():
            config = Config()
            config.domain = 'Source'
            config.name = 'DocumentName'
            config.value = source_doc
            sql_session.add(config)

        return get_source_document(sql_session)

    def get_plot_default(sql_session):
        # Get the last entered burial record with a non-null plot and use the plot as a default
        return Burial.get_last_plot(sql_session)

    def any_age_given(window):
        return window['-age_years-'].get() != '' or window['-age_months-'].get() != '' or window['-age_days-'].get() != ''

    def validate_age(window, values, id):
        value = values[id]
        for ndx in range(len(value)):
            if value[ndx] not in '0123456789':
                value = value[:ndx]
                window[id].update(value)
                break

    def validate_number(window, values, id):
        value = values[id]
        for ndx in range(len(value)):
            if value[ndx] not in '0123456789':
                value = value[:ndx]
                window[id].update(value)
                break

    def validate_reference(window, values, id):
        value = values[id]
        for ndx in range(len(value)):
            if value[ndx] not in '0123456789.':
                value = value[:ndx]
                window[id].update(value)
                break

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        app_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        exe_path = getattr(sys, 'executable', os.path.abspath(os.path.dirname(__file__)))
        db_path = os.path.join(os.path.dirname(exe_path), 'cards_log.db')
    else:
        app_path = os.path.abspath(os.path.dirname(__file__))
        exe_path = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(exe_path, 'cards_log.db')

    sql_engine = create_engine("sqlite+pysqlite:///" + db_path)

    sql_session = Session(sql_engine)

    must_create_db =  not os.path.exists(db_path)

    if must_create_db:
        create_db(sql_session)

    Base.prepare(sql_engine, reflect = True)

    if must_create_db:
        add_created_by(sql_session)

    source_document = get_source_document(sql_session)
    if not source_document:
        source_document = create_source_document(sql_session)

    Burial.set_default_plot(get_plot_default(sql_session))

    layout = Burial.gui_layout(source_document)

    window = sg.Window('Church Administration Records Database System - Log ' + VERSION, layout, text_justification = 'r', font = ('', 20), finalize = True) #, element_justification = 'c')

    Burial.gui_layout_new_record()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event in ('-given_names-', '-family_name-'):
            if len(values['-given_names-']) == 0 or len(values['-family_name-']) == 0:
                window['Save'].update(disabled = True)
            else:
                window['Save'].update(disabled = False)
        if event in ('-age_years-', '-age_months-', '-age_days-'):
            validate_age(window, values, event)
            if any_age_given(window):
                window['-stillborn-'].update(disabled = True)
            else:
                window['-stillborn-'].update(disabled = False)
        if event == '-stillborn-':
            if values['-stillborn-']:
                window['-age_years-'].update(disabled = True)
                window['#age_years#'].update(text_color = 'grey')
                window['-age_months-'].update(disabled = True)
                window['#age_months#'].update(text_color = 'grey')
                window['-age_days-'].update(disabled = True)
                window['#age_days#'].update(text_color = 'grey')
            else:
                window['-age_years-'].update(disabled = False)
                window['#age_years#'].update(text_color = 'black')
                window['-age_months-'].update(disabled = False)
                window['#age_months#'].update(text_color = 'black')
                window['-age_days-'].update(disabled = False)
                window['#age_days#'].update(text_color = 'black')
        if event == '-source_document_ref-':
            validate_reference(window, values, '-source_document_ref-')
        if event == '-cross_reference-':
            validate_reference(window, values, '-cross_reference-')
        if event == '-page_number-':
            validate_number(window, values, '-page_number-')
        if event == 'Save':
            if values['-given_names-'].rstrip() == '' or values['-family_name-'].rstrip() == '':
                sg.popup('Given names or family name cannot be blank')
            else:
                Burial.save(values)
        if event == 'Clear':
            Burial.gui_layout_new_record()

    sql_session.close()
