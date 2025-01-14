# build args
ARG SECRET_NPMRC
ARG DYNATRACE_ENABLED=0

#
# Drupal build
#
FROM drupal:9.3.16-php7.4-apache-buster AS drupal_build

# upgrade system + install required packages
RUN apt-get update -yq && \
    apt-get upgrade -yq && \
    apt-get install -yq \
      unzip \
      git \
      rsync \
      postgresql-client \
      python3 \
      python3-pip \
      procps && \
    pip3 install \
      jinja2-cli

# setup env vars
ENV APP_DIR=/opt/drupal
ENV SCRIPT_DIR=${APP_DIR}/scripts
ENV TEMPLATE_DIR=${APP_DIR}/templates
ENV I18N_DIR=${APP_DIR}/i18n
ENV WEB_DIR=${APP_DIR}/web
ENV SITE_DIR=${WEB_DIR}/sites
ENV MOD_DIR=${WEB_DIR}/modules
ENV THEME_DIR=${WEB_DIR}/themes
ENV CORE_DIR=${WEB_DIR}/core
ENV DATA_DIR=${SITE_DIR}/default/files
ENV WWW_DIR=/var/www

# copy app files
COPY i18n ${I18N_DIR}
COPY scripts ${SCRIPT_DIR}
COPY site_config ${APP_DIR}/site_config
COPY templates ${TEMPLATE_DIR}
COPY composer.json ${APP_DIR}/composer.json
COPY composer.lock ${APP_DIR}/composer.lock
RUN chmod +x ${SCRIPT_DIR}/*.sh && \
    mkdir -p ${SITE_DIR}/default/sync && \
    chown -R www-data:www-data ${SITE_DIR}/default/sync && \
    mkdir -p ${SITE_DIR}/default/files && \
    chown -R www-data:www-data ${SITE_DIR}/default/files

# install composer project
RUN composer install --no-cache


#
# Development image (For local development)
#
FROM drupal_build as drupal_development

ENV DEV_MODE=true

# install drupal dev requirements
RUN composer require --no-interaction --no-cache --dev drupal/devel

ENTRYPOINT ["/opt/drupal/scripts/entrypoint.sh"]

#
# Modules build (for production)
#
FROM ubuntu:focal AS modules_build

# install required packages
RUN apt-get update -yq && apt-get install -yq curl

# install nodejs via nodesource & frontend requirements
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get install -yq nodejs libjpeg-turbo8

# setup env vars:
ENV APP_DIR=/opt/drupal
ENV WEB_DIR=${APP_DIR}/web
ENV MOD_DIR=${WEB_DIR}/modules

# copy custom modules
RUN mkdir -p ${MOD_DIR} && mkdir -p ${WEB_DIR}/frontend
COPY modules/avoindata-header               ${MOD_DIR}/avoindata-header/
COPY modules/avoindata-servicemessage       ${MOD_DIR}/avoindata-servicemessage/
COPY modules/avoindata-hero                 ${MOD_DIR}/avoindata-hero/
COPY modules/avoindata-categories           ${MOD_DIR}/avoindata-categories/
COPY modules/avoindata-infobox              ${MOD_DIR}/avoindata-infobox/
COPY modules/avoindata-datasetlist          ${MOD_DIR}/avoindata-datasetlist/
COPY modules/avoindata-newsfeed             ${MOD_DIR}/avoindata-newsfeed/
COPY modules/avoindata-appfeed              ${MOD_DIR}/avoindata-appfeed/
COPY modules/avoindata-footer               ${MOD_DIR}/avoindata-footer/
COPY modules/avoindata-articles             ${MOD_DIR}/avoindata-articles/
COPY modules/avoindata-events               ${MOD_DIR}/avoindata-events/
COPY modules/avoindata-guide                ${MOD_DIR}/avoindata-guide/
COPY modules/avoindata-user                 ${MOD_DIR}/avoindata-user/
COPY modules/avoindata-ckeditor-plugins     ${MOD_DIR}/avoindata-ckeditor-plugins/
COPY modules/avoindata-theme                ${MOD_DIR}/avoindata-theme/

#
# Production stage, dynatrace enabled
#
FROM drupal_build AS production-dynatrace-1

# install dynatrace oneagent
# https://www.dynatrace.com/support/help/setup-and-configuration/setup-on-cloud-platforms/amazon-web-services/deploy-oneagent-on-aws-fargate
COPY --from=ayv41550.live.dynatrace.com/linux/oneagent-codemodules:php / /
ENV LD_PRELOAD=/opt/dynatrace/oneagent/agent/lib64/liboneagentproc.so

#
# Production stage, dynatrace disabled
#
FROM drupal_build AS production-dynatrace-0

# do nothing :^)

#
# Production image
#
FROM production-dynatrace-${DYNATRACE_ENABLED} AS production

# copy modules and themes
COPY --from=modules_build ${MOD_DIR} ${MOD_DIR}
RUN mv ${MOD_DIR}/avoindata-theme ${THEME_DIR}/avoindata/

ENTRYPOINT ["/opt/drupal/scripts/entrypoint.sh"]
