# LayIt — Build Partner Outreach Posts

All posts seek a hardware build partner for the LayIt Laser projection system.
Contact: layitapp@gmail.com

---

## 1. Reddit r/ESP32

**Title:** Looking for a build partner — ESP32-S3 driving dual-axis galvos for laser tile projection

**Body:**

I've designed a portable laser projection system that beams tile installation patterns onto walls/floors at 1:1 scale. The architecture:

- **ESP32-S3-WROOM-1** dual-core: Core 0 handles WiFi (receives vector data from phone app) + OV5640 camera (vision alignment). Core 1 runs a dedicated real-time galvo scan loop.
- **MCP4822 dual SPI DAC → TL072 op-amp buffer → 20Kpps XY galvo drivers** (ILDA interface)
- **200mW 520nm green laser module** with TTL modulation
- **MPU6050 IMU** for bump detection — if someone kicks the unit, camera re-locks to placed tile edges automatically
- **USB-C PD 12V input** → AMS1117-5.0 → AMS1117-3.3 (three rail supply)

The firmware partitioning is the interesting part — Core 1 can't have any jitter, so all WiFi/camera/vision processing is isolated on Core 0. DAC writes happen on a tight timer interrupt.

I have the full BOM ($237-$308 for the corded model), wiring diagrams, enclosure design, and a working app (PWA) that generates the vector paths. Three provisional patents filed.

Looking for someone who's built galvo-based projects and wants to co-develop the hardware side. This is a paid engagement with potential equity. Based in Minneapolis but remote works.

layitapp@gmail.com

---

## 2. Reddit r/lasers

**Title:** Need a galvo-experienced build partner — 200mW 520nm projection system (not a show laser)

**Body:**

Building something different from the usual ILDA show setup. This is a **utility projection system** — it projects tile installation patterns onto walls and floors at 1:1 scale so people can install tile without chalk lines or measuring.

Hardware specs:
- 200mW 520nm green, TTL modulated
- 20Kpps XY galvo set, ILDA interface
- Projection window ~3ft at working distance
- Needs to be daylight-visible (hence 200mW, not 50)
- Driven by MCP4822 DAC → TL072 buffer → galvo drivers
- ESP32-S3 as the controller

The vectors are simple — straight lines forming tile grids, cut boundaries, and grout lines. No complex curves or high-speed blanking patterns. But accuracy matters more than speed — we need <1mm positional consistency across the projection field.

I have the full system designed (BOM, wiring, enclosure, firmware architecture) and a working phone app that generates the projection data. Three patents filed. Looking for someone who knows galvo tuning, thermal management, and has built projector-class hardware before.

Paid project, potential equity component. Minneapolis-based, remote fine.

layitapp@gmail.com

---

## 3. Reddit r/AskElectronics

**Title:** Looking for a hardware build partner — laser + galvo + ESP32 projection system for tile installation

**Body:**

I've designed a consumer electronics product and need a build partner to bring it to life. It's a portable laser projector that beams tile layout patterns onto walls/floors at real-world scale — replacing chalk lines and tape measures for tile installation.

The system combines:
- ESP32-S3 microcontroller (dual-core, real-time constraints on one core)
- 200mW green laser with galvanometer XY scanning
- OV5640 camera module for computer vision alignment
- MPU6050 IMU for motion/bump detection
- SPI DAC → op-amp buffer → galvo driver signal chain
- USB-C PD power input, three regulated voltage rails

I have the complete design package: BOM (~$240-$310 per unit), wiring diagrams for all 5 assembly stages, 3D enclosure files, firmware architecture spec, and a working companion app. Three provisional patents filed.

What I need: someone experienced in mixed-signal PCB layout, laser/optics integration, and prototyping consumer hardware. Ideally someone who's taken a project from breadboard to small production run.

This is a paid engagement with potential equity. I'm in Minneapolis but open to remote collaboration.

layitapp@gmail.com

---

## 4. Minneapolis Hack Factory — Bulletin Board Post

**Title:** Looking for a Build Partner — Laser Tile Projection System

I'm building a laser projector that beams tile patterns onto walls and floors so you can install tile without measuring or chalk lines. Think of it as a 1:1 scale blueprint projected right on the surface.

The hardware side: ESP32-S3, green laser, galvanometer scanners, camera for auto-alignment, IMU for bump detection. I have the full design done — BOM, wiring diagrams, enclosure CAD, and a working phone app. Three patents filed.

I need someone local who's comfortable with soldering, mixed-signal circuits, and laser optics to help me build and iterate on the prototype. Paid project with potential for ongoing involvement.

If you've built anything with galvos, laser modules, or ESP32 and want to work on something with real commercial potential, let's grab coffee and talk.

Robbie — layitapp@gmail.com

---

## 5. Upwork Job Listing

**Title:** Hardware Engineer — Laser Projection System Prototype (ESP32 + Galvo)

**Category:** Engineering & Architecture > Electrical Engineering

**Budget:** $3,000–$8,000 (milestone-based, scope-dependent)

**Description:**

We're building a portable laser projection device that projects tile installation patterns onto walls and floors at 1:1 scale. The companion app (live, working) generates vector paths; the hardware renders them via laser + galvanometer scanning.

**System architecture:**
- ESP32-S3-WROOM-1 (dual-core: Core 0 = WiFi/camera/vision, Core 1 = real-time galvo loop)
- 200mW 520nm green laser module, TTL driver
- 20Kpps XY galvanometer scanner set, ILDA interface
- OV5640 5MP camera (vision-based alignment)
- MPU6050 6-axis IMU (bump detection)
- MCP4822 dual SPI DAC → TL072 op-amp buffer → galvo drivers
- USB-C PD 12V → dual LDO regulation (5V + 3.3V)

**What's already done:**
- Complete BOM with sourced components (~$240-$310/unit)
- 5-stage wiring diagrams (SVG)
- 3D enclosure design
- Firmware architecture specification
- Working companion app (PWA + iOS)
- 3 provisional patents filed

**What we need:**
1. Review and validate the existing hardware design
2. Build the first working prototype (we supply components or you source from BOM)
3. Write and test base firmware (galvo scan loop, WiFi vector receive, camera capture)
4. Iterate on calibration and projection accuracy (<1mm target)
5. Document build process for eventual small-batch production

**Required experience:**
- ESP32 firmware development (FreeRTOS, dual-core task pinning)
- Galvanometer or laser scanner systems
- Mixed-signal circuit design (SPI DAC, analog signal conditioning)
- Prototyping and soldering (through-hole and SMD)

**Nice to have:**
- OpenCV / embedded computer vision
- DFM experience (Design for Manufacturing)
- Consumer electronics product development

**Engagement type:** Milestone-based contract. Potential for ongoing role as we move to production. Three provisional patents protect the system — NDA required before sharing full design package.

**Contact:** layitapp@gmail.com
