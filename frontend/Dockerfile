FROM nginx:1.17.7-alpine

# Install used utilities
RUN apk add \
    wget \
    unzip

ARG ROOT_PATH=/usr/share/nginx/html
ARG VENDOR_PATH=$ROOT_PATH/vendor

RUN mkdir -p $VENDOR_PATH

# Install Font Awesome
ARG FONTAWESOME_VERSION=5.12.0
ARG FONTAWESOME_NAME=fontawesome-free-$FONTAWESOME_VERSION-web
ARG FONTAWESOME_ZIP=$FONTAWESOME_NAME.zip
ARG FONTAWESOME_URL=https://github.com/FortAwesome/Font-Awesome/releases/download/$FONTAWESOME_VERSION/$FONTAWESOME_ZIP

RUN wget -q $FONTAWESOME_URL \
    && unzip -q $FONTAWESOME_ZIP \
    && mv $FONTAWESOME_NAME $VENDOR_PATH/

# Install Bootstrap
ARG BOOTSTRAP_VERSION=4.3.1
ARG BOOTSTRAP_NAME=bootstrap-$BOOTSTRAP_VERSION-dist
ARG BOOTSTRAP_ZIP=$BOOTSTRAP_NAME.zip
ARG BOOTSTRAP_URL=https://github.com/twbs/bootstrap/releases/download/v$BOOTSTRAP_VERSION/$BOOTSTRAP_ZIP

RUN wget -q $BOOTSTRAP_URL \
    && unzip -q $BOOTSTRAP_ZIP \
    && mv $BOOTSTRAP_NAME $VENDOR_PATH/

# Install Darkly Bootstrap
ARG DARKLY_BOOTSTRAP_CSS=bootstrap.min.css
ARG DARKLY_BOOTSTRAP_URL=https://bootswatch.com/4/darkly/$DARKLY_BOOTSTRAP_CSS
ARG DARKLY_BOOTSTRAP_PATH=$VENDOR_PATH/darkly-bootstrap

RUN mkdir $DARKLY_BOOTSTRAP_PATH \
    && wget -q $DARKLY_BOOTSTRAP_URL \
    && mv $DARKLY_BOOTSTRAP_CSS $VENDOR_PATH/darkly-bootstrap/$DARKLY_BOOTSTRAP_CSS

# Install JQuery
ARG JQUERY_VERSION=3.4.1
ARG JQUERY_JS=jquery-$JQUERY_VERSION.slim.min.js
ARG JQUERY_URL=https://code.jquery.com/$JQUERY_JS
ARG JQUERY_PATH=$VENDOR_PATH/jquery

RUN mkdir $JQUERY_PATH \
    && wget -q $JQUERY_URL \
    && mv $JQUERY_JS $JQUERY_PATH/$JQUERY_JS

# Install Popper
ARG POPPER_VERSION=1.16.0
ARG POPPER_JS=popper.min.js
ARG POPPER_URL=https://cdn.jsdelivr.net/npm/popper.js@$POPPER_VERSION/dist/umd/$POPPER_JS
ARG POPPER_PATH=$VENDOR_PATH/popper-$POPPER_VERSION

RUN mkdir $POPPER_PATH \
    && wget -q $POPPER_URL \
    && mv $POPPER_JS $POPPER_PATH/$POPPER_JS

COPY index.html main.js main.css /usr/share/nginx/html/
