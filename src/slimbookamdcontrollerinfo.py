#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import gi
import subprocess
import utils

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from pathlib import Path
from gi.repository import Gtk, Gdk, GdkPixbuf     
from os.path import expanduser   


# AÑADIR CLASE --> .get_style_context().add_class("button-none")

#IDIOMAS ----------------------------------------------------------------

# pygettext -d slimbookamdcontrollercopy slimbookamdcontrollercopy.py

currpath = os.path.dirname(os.path.realpath(__file__))

_ = utils.load_translation('slimbookamdcontrollerinfo')

idiomas = utils.get_languages()[0]

user_name = subprocess.getoutput("logname")
user = subprocess.getoutput("echo ~"+user_name)


style_provider = Gtk.CssProvider()
style_provider.load_from_path(currpath+'/css/style.css')

Gtk.StyleContext.add_provider_for_screen (
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

class PreferencesDialog(Gtk.Dialog):
	
    def __init__(self):
		
        Gtk.Dialog.__init__(self,
			title='',
            parent=None,
            flags=0)

        #Botones de aceptar y cerrar
        #self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        #self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        ICON = (currpath+'/images/slimbookamdcontroller.svg')
        #print('Ruta icono: '+ICON)
        
        try: 
            self.set_icon_from_file(ICON)
        except:
            print("Not found")

        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)     
        self.get_style_context().add_class("bg-color")
        self.set_default_size(900, 0)     
        self.set_decorated(False)

        vbox = Gtk.VBox(spacing=5)
        vbox.set_border_width(5)

        self.get_content_area().add(vbox)

        # Icono APP
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
			filename= currpath+'/images/logo-sb.png',
			width=200,
			height=100,
			preserve_aspect_ratio=True)
        iconApp = Gtk.Image.new_from_pixbuf(pixbuf)
        iconApp.set_name('top')


        info = Gtk.Label()
        info.set_markup('<span>'+(_("The Slimbook AMD Controller app is capable of setting several TDP power levels for your AMD Ryzen mobile processor. Switching between the different performance presets will give you the ability to control both performance and battery life with a single click. Bear in mind that the higher you set your performance level, your processor will also run hotter and drain your battery faster, so keep that in mind! \n\nSlimbook AMD Controller uses the third party software RyzenAdj from FlyGoat."))+'</span>')
        info.set_line_wrap(True)
        info.set_name('label')
        info.set_name('info')
        
        info2 = Gtk.Label()
        info2.set_markup('<span>'+_("If you want to support the Slimbook team with the development of this app and several more to come, you can do so by joining our ") + "<a href='https://www.patreon.com/slimbook'> patreon </a>" +_(" or buying a brand new Slimbook.")+'</span>')
        info2.set_line_wrap(True)
        info2.set_name('label')
        info2.set_name('info')

        info3 = Gtk.Label()
        info3.set_markup("<span><b>"+_("Note: ")+"</b>"+_("Many laptops limit the power of the CPU, when working without the charger connected. Therefore, if you want to take advantage of the high-performance mode of this application, you may need to connect the charger.")+"</span>")
        info3.set_line_wrap(True)
        info3.set_name('label')
        info3.set_name('info')

        
        enlaces_box = Gtk.Box(spacing=5)
        enlaces_box.set_halign(Gtk.Align.CENTER)

        salvavidas = Gtk.Label(label=_('This software is provided * as is * without warranty of any kind..'))
        salvavidas.set_name('label')

        license1 = Gtk.Label()
        license1.set_markup("<span><b>"+_("You are free from:")+"</b></span>")
        license1.set_name('label')

        license2 = Gtk.Label()
        license2.set_markup("<span><b><small>"+_("Share: ")+"</small></b><small>"+_("copy and redistribute the material in any medium or format\nSlimbook Copyright - License Creative Commons BY-NC-ND")+"</small></span>")
        license2.set_name('label')

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
			filename=currpath+'/images/cc.png',
			width=100,
			height=50,
			preserve_aspect_ratio=True)

        licencia = Gtk.Image.new_from_pixbuf(pixbuf)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
			filename=currpath+'/images/cross.png',
			width=20,
			height=20,
			preserve_aspect_ratio=True)

        close = Gtk.Image.new_from_pixbuf(pixbuf)
        close.set_halign(Gtk.Align.END)

        evnt_close = Gtk.EventBox()
        evnt_close.add(close)
        evnt_close.connect("button_press_event", self.on_button_close)

    # REDES SOCIALES --------------------------------------------------------------
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
			filename=currpath+'/images/twitter.png',
			width=25,
			height=25,
			preserve_aspect_ratio=True)

        itwitter = Gtk.Image.new_from_pixbuf(pixbuf)
        enlaces_box.pack_start(itwitter, False, False, 0)

        twitter = Gtk.Label()
        twitter.set_markup("<span><b><a href='https://twitter.com/SlimbookEs'>@SlimbookEs</a></b>    </span>")
        twitter.set_justify(Gtk.Justification.CENTER)
        
        enlaces_box.pack_start(twitter, False, False, 0)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
			filename=currpath+'/images/facebook.png',
			width=25,
			height=25,
			preserve_aspect_ratio=True)

        ifacebook = Gtk.Image.new_from_pixbuf(pixbuf)
        enlaces_box.pack_start(ifacebook, False, False, 0)

        facebook = Gtk.Label()
        facebook.set_markup("<span><b><a href='https://www.facebook.com/slimbook.es'>slimbook.es</a></b>    </span>")
        facebook.set_justify(Gtk.Justification.CENTER)
        enlaces_box.pack_start(facebook, False, False, 0)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
			filename=currpath+'/images/insta.png',
			width=25,
			height=25,
			preserve_aspect_ratio=True)

        iinstagram = Gtk.Image.new_from_pixbuf(pixbuf)
        enlaces_box.pack_start(iinstagram, False, False, 0)

        instagram = Gtk.Label()
        instagram.set_markup("<span><b><a href='https://www.instagram.com/slimbookes'>@slimbookes</a></b></span>")
        instagram.set_justify(Gtk.Justification.CENTER)
        enlaces_box.pack_start(instagram, False, False, 0)

    # Enlaces --------------------------------------------------------------------------
        
        link_box2 = Gtk.HBox()
        link_box2.set_halign(Gtk.Align.CENTER)

        #WEB
        web_link=''
        print(idiomas)
        if idiomas.find('es') >= 0:
            web_link = 'https://slimbook.es/es/'
        else:
            web_link = 'https://slimbook.es/en/'

        #TUTORIAL
        tutorial_link=''
        if idiomas.find('es') >= 0:
            tutorial_link = 'https://slimbook.es/es/tutoriales/aplicaciones-slimbook/493-slimbook-amd-controller'
        else:
            tutorial_link = 'https://slimbook.es/en/tutoriales/aplicaciones-slimbook/494-slimbook-amd-controller-en'

        label77 = Gtk.LinkButton(uri=web_link, label =_("Visit @Slimbook web"))
        label77.set_name('link')
        label77.set_halign(Gtk.Align.CENTER)
        link_box2.add(label77)

        label77 = Gtk.LinkButton(uri=tutorial_link, label = (_("@SlimbookAMDController Tutorial")))
        label77.set_name('link')
        label77.set_halign(Gtk.Align.CENTER)
        link_box2.add(label77)

        label77 = Gtk.LinkButton(uri="https://github.com/slimbook/slimbookamdcontroller/tree/main/src/locale", label = (_('Help us with translations!')))
        label77.set_name('link')
        label77.set_halign(Gtk.Align.CENTER)
        link_box2.add(label77)

        email = Gtk.Label()
        email.set_markup("<span><b>"+_("Send an e-mail a: ")+"dev@slimbook.es</b></span>")
        email.set_justify(Gtk.Justification.CENTER)
        email.set_name('label')

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename= os.path.join(currpath+'/images/', 'GitHub_Logo_White.png'),
            width=150,
            height=30,
            preserve_aspect_ratio=True)

        img = Gtk.Image()
        img.set_from_pixbuf(pixbuf)
        
        github = Gtk.LinkButton(uri="https://github.com/slimbook/slimbookamdcontroller")
        github.set_name('link')
        github.set_halign(Gtk.Align.CENTER)
        github.set_image(img)

    
    # PACKKING ----------------------------------------------------------------------

        vbox.pack_start(evnt_close,True, True, 0)
        vbox.pack_start(iconApp, True, True, 20)

        vbox.pack_start(info, True, True, 20)
        
        vbox.pack_start(enlaces_box, True, True, 5)
        vbox.pack_start(link_box2, True, True, 10)
        vbox.pack_start(github, True, True, 0)
        vbox.pack_start(email, True, True, 10)
        vbox.pack_start(salvavidas, True, True, 0)

        vbox.pack_start(license1, True, True, 0)
        vbox.pack_start(license2, True, True, 0)
        vbox.pack_start(licencia, True, True, 10)
        vbox.pack_start(info2, True, True, 20)
        vbox.pack_start(info3,True, True, 0)

        #SHOW
        self.show_all()
    
    def on_buttonCopyEmail_clicked(self, buttonCopyEmail):
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.clipboard.set_text('dev@slimbook.es', -1)
        os.system("notify-send 'Slimbook AMD Controller' "+_("'The email has been copied to the clipboard'") + " -i '" + currpath + "/images/icono.png'")

    def on_button_close(self, button, state):
        self.close()
        self.hide()
        self.destroy()
        Gtk.main_quit




