FROM node:latest as node_build
RUN mkdir /work_area
WORKDIR /work_area
COPY frontend/package.json frontend/package-lock.json ./
RUN npm clean-install # installs from package-lock
COPY frontend .
RUN npx next build

FROM python:3.10-slim-bookworm
RUN apt update
RUN apt install -y nginx
RUN pip install pipenv
WORKDIR /usr/src/app/backend
COPY  ./backend/Pipfile ./backend/Pipfile.lock ./
RUN pipenv sync
WORKDIR /usr/src/app
COPY launch.sh .
COPY nginx nginx/
COPY backend backend/
COPY --from=node_build /work_area/out /usr/src/app/nginx/static/
ENV TORNADO_PORT 8001
ENV NGINX_PORT 8000
EXPOSE ${NGINX_PORT}/tcp
ENTRYPOINT [ "./launch.sh" ]
