import os
from dotenv import load_dotenv
import flet as ft
from flet import ElevatedButton, LoginEvent, Page
from flet.auth.providers import GitHubOAuthProvider

# Get client ID and client secret:
load_dotenv()
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

def main(page: Page):
    provider = GitHubOAuthProvider(
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        redirect_url="http://localhost:8550/api/oauth/redirect",
    )

    def login_button_click(e):
        page.login(provider, scope=["public_repo"])

    def logout_button_click(e):
        page.logout()

    def on_login(e: LoginEvent):
        if not e.error:
            # toggle_login_buttons()
            # print(page.auth.user.id)
            # login_button.visible = False
            page.redirect('/login?user_id=' + str(page.auth.user.id))

    def on_logout(e):
        logout_button.visible = page.auth is not None

    login_button = ElevatedButton("Login with GitHub", on_click=login_button_click)
    logout_button = ElevatedButton("Logout", on_click=logout_button_click)
    page.on_login = on_login
    page.on_logout = on_logout
    page.add(login_button, logout_button)

    return page

# ft.app(target=main, port=8550, view=ft.WEB_BROWSER)