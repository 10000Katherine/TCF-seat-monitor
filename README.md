# TCF Seat Monitor

A simple Python tool that monitors **TCF Canada exam seat availability** and sends an email notification when a seat may become available.

This tool helps candidates avoid constantly refreshing the booking pages when trying to secure a TCF exam slot.

---

## Features

- Automatic monitoring of TCF exam pages
- Email notification when seat availability changes
- Simple GUI interface
- Monitor multiple test centers
- Adjustable check interval
- Activity logging

---

## Supported Locations

Currently supports monitoring:

- Alliance Française Vancouver  
- AF Victoria  
- Ashton Testing  

You can modify or add new locations in `targets.json`.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/10000Katherine/TCF-seat-monitor.git
cd TCF-seat-monitor

Install dependencies:
    pip install -r requirements.txt

Run the GUI version:
    python gui_monitor.py
