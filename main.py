from flet import *
import asyncio

async def main(page: Page):
    page.bgcolor = "#2C2C2C"
    page.title = "Med Tracker"
    page.window_width = 320
    page.window_height = 650

    def switch_to_welcome(e=None):
        # Capsule images for the welcome page
        capsule_positions = [
            (0, 10), (60, 12), (160, 15), (250, 8),
            (0, 102), (90, 115), (165, 120), (250, 100),
            (0, 210), (100, 220), (190, 230), (250, 190)
        ]

        capsules = [
            Container(
                content=Image(src=f"capsule_{i + 1}.png", width=50, height=50, fit="contain"),
                left=pos[0],
                top=pos[1],
                width=90,
                height=90
            )
            for i, pos in enumerate(capsule_positions)
        ]

        def go_to_login(e):
            print("Navigating to Login Page")
            # Replace the following with your logic to navigate to the login page
            login_page = Container(
                content=Text(value="Login Page Placeholder", size=24, color="white"),
                width=320,
                height=650,
                bgcolor="#2C2C2C",
                alignment=alignment.center
            )
            outer_container.content = login_page
            page.update()

        # Welcome page content
        welcome_page = Container(
            width=320,
            height=650,
            bgcolor="#26A69A",
            border_radius=35,
            content=Stack(
                controls=[
                    *capsules,
                    Container(
                        width=320,
                        height=650,
                        padding=padding.symmetric(horizontal=20),
                        content=Column(
                            controls=[
                                Container(
                                    margin=margin.only(top=355),
                                    content=Text(
                                        value="Your personal \n assistant, but for \nyour pills!",
                                        size=22,
                                        color="white",
                                        weight=FontWeight.BOLD,
                                        text_align=TextAlign.CENTER,
                                    ),
                                ),
                                Container(
                                    margin=margin.only(top=5, bottom=25),
                                    content=Text(
                                        value="Your daily dose, perfectly \non time.",
                                        size=16,
                                        color="white",
                                        text_align=TextAlign.CENTER,
                                    ),
                                ),
                                Container(
                                    width=200,
                                    height=45,
                                    content=ElevatedButton(
                                        content = Text(
                                            value = "Sign Up",
                                            text_align=TextAlign.CENTER,
                                            weight=FontWeight.BOLD
                                        ),
                                        bgcolor="#E0F2F1",
                                        color="black",
                                        width=200,
                                        on_click=lambda _: print("Sign Up Clicked!"),
                                    ),
                                ),
                                Container(
                                    margin=margin.only(top=10),
                                    content=TextButton(
                                        text="Already have an account? Login",
                                        on_click=go_to_login,
                                        style=ButtonStyle(
                                            color="white",
                                            text_style=TextStyle(size=14),
                                        ),
                                    ),
                                ),
                            ],
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.START,
                        ),
                    ),
                ],
            ),
        )

        # Replace the loading page with the welcome page
        outer_container.content = welcome_page
        page.update()

    # Loading page with a logo and initial message
    phone_container = Container(
        width=320,
        height=650,
        bgcolor="#E0F2F1",
        border_radius=35,
        content=Column(
            controls=[
                Image(
                    src="logo.png",
                    width=200,
                    height=200,
                ),
                Text(
                    value="Stay on Track,\nStay Healthy!!",
                    size=24,
                    color="black",
                    weight=FontWeight.BOLD,
                    text_align=TextAlign.CENTER,
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        ),
    )

    outer_container = Container(
        content=phone_container
    )

    page.add(outer_container)

    async def delayed_switch():
        await asyncio.sleep(3)
        switch_to_welcome()

    await delayed_switch()

app(target=main)