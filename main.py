"""
Open Copr projects in the web browser
https://copr.fedorainfracloud.org/
"""

from copr.v3 import Client
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.RenderResultListAction \
    import RenderResultListAction


class CoprExtension(Extension):
    """
    Open Copr projects in the web browser
    """

    def __init__(self):
        super(CoprExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    """
    When user enters a query that starts with "copr "
    This event is re-triggered every time a new letter is typed.
    """

    def __init__(self):
        super(KeywordQueryEventListener, self).__init__()
        self.copr_client = Client.create_from_config_file()
        self.projects = []

    def on_event(self, event, extension):
        query = event.get_argument()
        if not query or not self.projects:
            self.projects = self.copr_projects()

        projects = self.search(query)
        result = [self.project_to_ulauncher_result(x) for x in projects]
        return RenderResultListAction(result)

    @property
    def username(self):
        """
        Return my Copr username based on `~/.config/copr`
        """
        config = self.copr_client.config
        if config.get("username"):
            return config["username"]
        if config.get("gssapi"):
            return self.copr_client.base_proxy.auth_username()
        return None

    def copr_projects(self):
        """
        Return a list of all Copr projects for the current user
        """
        return self.copr_client.project_proxy.get_list(self.username)

    def search(self, query):
        """
        Filter the list of all Copr projects based on the query string.
        I bet ulauncher has some built-in fuzzy finding function already.
        """
        if not query:
            return self.projects
        query = query.strip().lower()
        return [x for x in self.projects if query in x.full_name.lower()]

    def project_url(self, project):
        """
        Return a fully qualified URL for a given Copr project
        """
        instance = self.copr_client.config["copr_url"]
        return "{0}/coprs/{1}".format(instance, project.full_name)

    def project_to_ulauncher_result(self, project):
        """
        Convert a Copr project to an `ExtensionResultItem`
        """
        action = OpenUrlAction(self.project_url(project))
        return ExtensionResultItem(
            icon="images/icon.png",
            name=project.full_name,
            on_enter=action,
        )


if __name__ == "__main__":
    CoprExtension().run()
