
import os
import sys
import psutil


# Based on http://stackoverflow.com/a/21213358/1530134
def get_desktop_environment():
    # From http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=1139057
    if sys.platform in ['win32', 'cygwin']:
        return 'windows'
    elif sys.platform == 'darwin':
        return 'mac'
    else:  # Most likely either a POSIX system or something not much common
        desktop_session = os.environ.get('DESKTOP_SESSION')
        if desktop_session is None or desktop_session.lower() == 'default':
            desktop_session = os.environ.get('XDG_CURRENT_DESKTOP')
        # Easier to match if we don't have to deal with character cases
        if desktop_session is not None:
            desktop_session = desktop_session.lower()
            if desktop_session in {
                    'gnome', 'unity', 'cinnamon', 'mate', 'xfce4', 'lxde', 'fluxbox',
                    'blackbox', 'openbox', 'icewm', 'jwm', 'afterstep', 'trinity', 'kde'}:
                return desktop_session

            # TODO: FIX FOR KDE 5 (PLASMA)
            # == Special cases == #
            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
            # There is no guarantee that they will not do the same with the other desktop environments.
            elif 'xfce' in desktop_session or desktop_session.startswith('xubuntu'):
                return 'xfce4'
            elif desktop_session.startswith('ubuntu'):
                return 'unity'
            elif desktop_session.startswith('lubuntu'):
                return 'lxde'
            elif desktop_session.startswith('kubuntu'):
                return 'kde'
            elif desktop_session.startswith('razor'):  # e.g. razorkwin
                return 'razor-qt'
            elif desktop_session.startswith('wmaker'):  # e.g. wmaker-common
                return 'windowmaker'
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            return 'kde'
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            if 'deprecated' not in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return 'gnome2'
        # From http://ubuntuforums.org/showthread.php?t=652320
        elif is_process_running('xfce-mcs-manage'):
            return 'xfce4'
        elif is_process_running('ksmserver'):
            return 'kde'
    return 'unknown'


def is_process_running(process_name):
    return any(proc.name == process_name for proc in psutil.process_iter())
