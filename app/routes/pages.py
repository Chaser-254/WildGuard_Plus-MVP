from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

def render_coming_soon(page_name):
    return render_template('pages/coming_soon.html', page_name=page_name)

@pages_bp.route('/about')
def about():
    return render_template('pages/about.html')

@pages_bp.route('/contact')
def contact():
    return render_template('pages/contact.html')

@pages_bp.route('/help')
def help():
    return render_template('pages/help.html')

@pages_bp.route('/detections')
def detections():
    return render_coming_soon('Detections')

@pages_bp.route('/cameras')
def cameras():
    return render_coming_soon('Cameras')

@pages_bp.route('/rangers')
def rangers():
    return render_coming_soon('Rangers')

@pages_bp.route('/reports')
def reports():
    return render_coming_soon('Reports')

@pages_bp.route('/settings')
def settings():
    return render_coming_soon('Settings')