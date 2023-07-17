import uvicorn

from social.routes.base import app


if __name__ == '__main__':
    uvicorn.run(app)
