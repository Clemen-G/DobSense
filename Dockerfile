# hardcoding platform since this stage only produces static assets
FROM --platform=linux/amd64 node:latest as node_build
RUN mkdir /work_area
WORKDIR /work_area
COPY frontend/package.json frontend/package-lock.json ./
RUN npm clean-install --loglevel verbose  # installs from package-lock
COPY frontend .
RUN npx next build

FROM python:3.10-slim-bookworm
RUN apt update
RUN apt install -y nginx
# temp
RUN apt install -y vim
RUN pip install pipenv
WORKDIR /usr/src/app/backend
COPY  ./backend/Pipfile ./backend/Pipfile.lock ./
RUN pipenv sync
WORKDIR /usr/src/app
COPY launch.dev.sh .
COPY launch.prod.sh .
COPY nginx nginx/
COPY backend backend/
COPY --from=node_build /work_area/out /usr/src/app/nginx/static/
ENV TORNADO_PORT 8001
ENV NGINX_HTTP_PORT 8080
ENV NGINX_HTTPS_PORT 8443
EXPOSE ${NGINX_HTTP_PORT}/tcp ${NGINX_HTTPS_PORT}/tcp
ENTRYPOINT [ "./launch.prod.sh" ]
