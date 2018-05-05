import os
import aiohttp

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """
    Whenever an issue is opened, greet the author and say thanks.
    """
    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]

    message = f"Thanks for the report @{author}! I will look into it ASAP! (I'm a bot)."
    await gh.post(url, data={"body": message})


@router.register("pull_request", action="closed")
async def pull_request_event(event, gh, *args, **kwargs):
    """
    Whenever a pull request is merged, say thanks.
    """
    url = event.data["pull_request"]["comments_url"]
    merged = event.data["pull_request"]["merged"]
    if merged:
        message = f"Thanks for merging this pr! (I'm a bot)."
        await gh.post(url, data={"body": message})


@router.register("issue_comment", action="created")
async def issue_opened_event(event, gh, *args, **kwargs):
    print(event.data)
    url = event.data["comment"]["url"]

    author = event.data["comment"]["user"]["login"]

    #if author == "jeanettejohnson":
    await gh.post(url, data={"content": "hooray"}, accept={"application/vnd.github.squirrel-girl-preview+json"})


async def main(request):
    body = await request.read()

    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    event = sansio.Event.from_http(request.headers, body, secret=secret)
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "jeanettejohnson",
                                  oauth_token=oauth_token)
        await router.dispatch(event, gh)
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
