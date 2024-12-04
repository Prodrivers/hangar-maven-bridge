ARG UNIT_VARIANT=1.33.0-python3.12-slim

# Initialize virtual environement in a separate build image
# We want to minimize work in target platform image as much as possible as it may run under emulation.
# Since pip is going to install platform-specific packages, it is easier to just run it under the target platform.
# With this, we are still going to reduce the final image's size.
FROM --platform=$TARGETPLATFORM unit:${UNIT_VARIANT} AS builder-target
LABEL stage=builder

# Copy application files
ADD ./pyproject.toml /app/pyproject.toml
ADD ./app /app/app

# Change work directory to application
WORKDIR /app

# Create virtual environement
RUN python3 -m venv /venv

# Install dependencies in virtual environement
RUN /bin/bash -c "source /venv/bin/activate && pip install ."

# Build final image, with target platform
FROM --platform=$TARGETPLATFORM unit:${UNIT_VARIANT}

# Copy application files from build image
COPY --from=builder-target /app /app

# Copy virtual environment from build image
COPY --from=builder-target /venv /app/venv

# Copy NGINX Unit configuration
COPY ./nginx/* /docker-entrypoint.d/

# Change work directory to application
WORKDIR /app
