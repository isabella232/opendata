from ckan.common import _, c
from ckan.lib import helpers
from collections import OrderedDict
from ckan.logic import NotFound
from ckan.plugins.core import get_plugin

""" Menu class structure. The structure is complex, because cross linking between Drupal and CKAN can be expected.
    Menu generation is subset of Drupal menu from API.
"""


class MenuItem(object):
    title = None
    children = []
    selected = False
    requires_login = False

    def link(self):
        return "#"

    def select(self, selected_class):
        if isinstance(self, selected_class):
            self.selected = True
        else:
            for child in self.children:
                child.select(selected_class)

        return self

    def to_drupal_dictionary(self):
        data = {'selected': self.selected,
                'link': {
                    'href': self.link(),
                    'title': self.title}}

        if not self.children:
            data['children'] = []
        else:
            data['children'] = OrderedDict()
            for child in self.children:
                if child.requires_login and not c.user:
                    continue
                data['children'][child.title] = child.to_drupal_dictionary()
        return data


class RootMenuItem(MenuItem):
    def __init__(self, plugin):
        self.plugin = plugin

    def to_drupal_dictionary(self):
        data = super(RootMenuItem, self).to_drupal_dictionary()
        return data['children']


class MyDatasetsMenu(MenuItem):
    def __init__(self):
        super(MyDatasetsMenu, self).__init__()
        self.title = _("Datasets")
        self.requires_login = True

    def link(self):
        return helpers.url_for('user_dashboard_datasets')


class MyOrganizationMenu(MenuItem):
    def __init__(self):
        super(MyOrganizationMenu, self).__init__()
        self.title = _("Organizations")
        self.requires_login = True

    def link(self):
        return helpers.url_for('user_dashboard_organizations')


class MyPersonalDataMenu(MenuItem):
    def __init__(self):
        super(MyPersonalDataMenu, self).__init__()
        self.title = _("Personal Data")
        self.requires_login = True

    def link(self):
        return helpers.url_for('user_edit', id=c.user)


class MyInformationMenu(MenuItem):
    def __init__(self, children=True):
        super(MyInformationMenu, self).__init__()
        self.title = _("My Information")
        if children:
            self.children = [MyPersonalDataMenu(), MyOrganizationMenu(), MyDatasetsMenu()]
        self.requires_login = True

    def link(self):
        return helpers.url_for('user_datasets', id=c.user)


class MyPasswordMenu(MenuItem):
    def __init__(self, plugin):
        super(MyPasswordMenu, self).__init__()
        self.title = _("User Account")
        self.plugin = plugin
        self.requires_login = True

    def link(self):
        try:
            ytp_drupal = get_plugin('ytp_drupal')
            if ytp_drupal or not c.user:
                raise NotFound
            return "/%s/user/%s/edit" % (helpers.lang(), str(ytp_drupal.get_drupal_user_id(c.user)))
        except NotFound:
            return "/"


class MyCancelMenu(MenuItem):
    def __init__(self):
        super(MyCancelMenu, self).__init__()
        self.title = _("Cancel account")
        self.requires_login = True

    def link(self):
        return helpers.url_for('user_delete_me')


class UserMenu(RootMenuItem):
    def __init__(self, plugin):
        super(UserMenu, self).__init__(plugin)
        self.children = [MyInformationMenu(), MyPasswordMenu(plugin), MyCancelMenu()]


class ListUsersMenu(MenuItem):
    def __init__(self):
        super(ListUsersMenu, self).__init__()
        self.title = _("Users")
        self.requires_login = True

    def link(self):
        return helpers.url_for('user_index')


class OrganizationMenu(MenuItem):
    def __init__(self):
        super(OrganizationMenu, self).__init__()
        self.title = _("Organizations")

    def link(self):
        return helpers.url_for('organizations_index')


class ProducersMenu(RootMenuItem):
    def __init__(self, plugin):
        super(ProducersMenu, self).__init__(plugin)
        self.children = [OrganizationMenu(), ListUsersMenu(), MyInformationMenu(children=False)]