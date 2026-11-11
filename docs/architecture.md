# System Architecture

## Overview

HydroDAQ is designed as a modular data acquisition and analysis system.

## Planned Data Flow

Sensors
  ↓
Embedded Acquisition (C)
  ↓
Data Transmission
  ↓
Python Ingestion and Processing
  ↓
SQL Database
  ↓
Engineering Analysis and Visualization

## Development Approach

Development begins with recorded hydraulic sensor measurements to establish the processing, storage, and analysis pipeline.

Hardware-based acquisition will be introduced as a subsequent development phase.