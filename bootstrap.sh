#!/bin/sh

# Bootstrapping steps. Here we create needed directories on the guest
mkdir -p ~/.ssh
mkdir -p -m777 ~/.ansible
mkdir -p -m777 ~/.config
mkdir -p -m777 ~/.config/openstack

