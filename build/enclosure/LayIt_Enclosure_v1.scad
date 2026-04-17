// ============================================================
// LayIt Laser — Hex Flying Saucer Enclosure v4
// COMPACT: ~6" across, ~3.3" tall
// Six flat edge walls + convex dome top & bottom
// Designed for removable silicone sleeve
// ============================================================

// ----- PRINT SETTINGS -----
// Layer height: 0.2mm | Infill: 25% | Supports: Yes
// Material: PETG (heat resistant) or PLA (prototype)
// Post-process: Silicone sleeve (Ecoflex 00-30), NOT Plasti Dip

// ============================================================
// MASTER DIMENSIONS
// ============================================================

hex_radius     = 75;     // ~150mm / 5.9" across (down from 7.5")
corner_radius  = 15;
wall_thickness = 3;

total_height   = 85;     // 3.3" tall (up from 2.75")
edge_height    = 50;     // flat edge wall height
// dome_bulge = (85 - 50) / 2 = 17.5mm per side

split_ratio    = 0.55;

lip_height     = 3;
lip_inset      = 1.5;
lip_tolerance  = 0.3;

// ----- COMPONENT DIMENSIONS -----
galvo_width    = 55;
galvo_depth    = 50;
galvo_height   = 45;

driver_length  = 78;
driver_width   = 55;
driver_height  = 27;

esp32_length   = 70;
esp32_width    = 28;
esp32_height   = 12;

laser_width    = 40;
laser_depth    = 60;
laser_height   = 40;
laser_aperture = 18;

cam_lens_dia   = 14;
usb_c_width    = 8.94;
usb_c_height   = 3.26;
vent_hole_dia    = 4;     // perforated hole diameter
vent_grid_cols   = 5;     // holes per row
vent_grid_rows   = 5;     // rows per vent zone
vent_spacing     = 8;     // center-to-center hole spacing

tripod_insert_dia = 8;
tripod_insert_depth = 12;

screw_dia      = 3.4;
screw_head_dia = 6;
insert_dia     = 4.2;
num_screws     = 6;

// ----- EXHAUST FAN -----
fan_size         = 30;   // 30mm fan (cheap, quiet, plenty for 5-9W heat)
fan_screw_spacing = 24;  // M3 mounting hole spacing (30mm fan standard)
fan_depth        = 10;   // fan body depth

// ----- SLEEVE DIMENSIONS -----
sleeve_thickness = 3.5;  // silicone wall thickness
sleeve_gap       = 0.5;  // clearance between enclosure and sleeve

// ============================================================
// QUALITY
// ============================================================
$fn = 15;  // LOW for smooth preview. Bump to 80 before exporting STL for print

// ============================================================
// DERIVED VALUES
// ============================================================
dome_bulge = (total_height - edge_height) / 2;  // 17.5mm
edge_bottom = dome_bulge;
edge_top = dome_bulge + edge_height;
split_z = edge_bottom + edge_height * split_ratio;
vent_start_z = edge_bottom + (edge_height - (vent_grid_rows - 1) * vent_spacing) / 2;
screw_post_r = hex_radius * cos(30) - screw_head_dia/2 - 1;  // keep countersinks inside the wall

// ============================================================
// MODULES
// ============================================================

module rounded_hex(radius, rounding) {
    offset(r = rounding)
    offset(r = -rounding)
    circle(r = radius, $fn = 6);
}

module hex_prism(radius, rounding, height) {
    linear_extrude(height = height)
    rounded_hex(radius, rounding);
}

// Flying saucer shape — flat hex edges + dome top/bottom
module saucer_solid(rad, cr, th, eh, db) {
    hull() {
        // Bottom dome peak
        translate([0, 0, 0])
        linear_extrude(height = 0.01)
        rounded_hex(rad * 0.5, cr + 15);

        // Bottom of edge walls
        translate([0, 0, db])
        linear_extrude(height = 0.01)
        rounded_hex(rad, cr);

        // Top of edge walls
        translate([0, 0, db + eh])
        linear_extrude(height = 0.01)
        rounded_hex(rad, cr);

        // Top dome peak
        translate([0, 0, th])
        linear_extrude(height = 0.01)
        rounded_hex(rad * 0.5, cr + 15);
    }
}

// Main enclosure saucer
module enclosure_saucer() {
    saucer_solid(hex_radius, corner_radius, total_height, edge_height, dome_bulge);
}

// Interior cavity
module interior_cavity() {
    translate([0, 0, wall_thickness + dome_bulge])
    hex_prism(hex_radius - wall_thickness, corner_radius, edge_height - wall_thickness);
}

// ============================================================
// BOTTOM HALF
// ============================================================
module bottom_half() {
    difference() {
        union() {
            intersection() {
                enclosure_saucer();
                translate([0, 0, split_z/2])
                cube([hex_radius * 3, hex_radius * 3, split_z], center = true);
            }

            // Alignment lip
            translate([0, 0, split_z])
            difference() {
                hex_prism(hex_radius - wall_thickness + 0.01, corner_radius, lip_height);
                hex_prism(hex_radius - wall_thickness - lip_inset, corner_radius, lip_height + 1);
            }
        }

        interior_cavity();

        // ----- SCREWS (countersunk from bottom) -----
        for (i = [0:num_screws-1]) {
            angle = i * 360 / num_screws;
            translate([screw_post_r * cos(angle), screw_post_r * sin(angle), 0]) {
                cylinder(d = screw_dia, h = split_z + lip_height + 1);
                translate([0, 0, -0.1])
                cylinder(d = screw_head_dia, h = dome_bulge + 3);
            }
        }

        // ----- TRIPOD MOUNT -----
        translate([0, 0, -0.1])
        cylinder(d = tripod_insert_dia, h = tripod_insert_depth + dome_bulge + 0.1);

        // ----- FRONT (+Y): LASER APERTURE -----
        translate([0, hex_radius + 1, edge_bottom + edge_height/2])
        rotate([90, 0, 0])
        cylinder(d = laser_aperture, h = wall_thickness + 10);

        // ----- FRONT: CAMERA -----
        translate([30, hex_radius + 1, edge_bottom + edge_height/2 - 2])
        rotate([90, 0, 0])
        cylinder(d = cam_lens_dia, h = wall_thickness + 10);

        // ----- FRONT: STATUS LED -----
        translate([-30, hex_radius + 1, edge_bottom + edge_height/2 - 2])
        rotate([90, 0, 0])
        cylinder(d = 6, h = wall_thickness + 10);

        // ----- BACK (-Y): USB-C PORT -----
        translate([-20, -(hex_radius + 1), edge_bottom + edge_height/2])
        rotate([-90, 0, 0])
        hull() {
            translate([-(usb_c_width/2 - usb_c_height/2), 0, 0])
            cylinder(d = usb_c_height, h = wall_thickness + 10);
            translate([(usb_c_width/2 - usb_c_height/2), 0, 0])
            cylinder(d = usb_c_height, h = wall_thickness + 10);
        }

        // (Fan mount removed — fan mounts internally, airflow is side intake → top dome exhaust)

        // ----- PERFORATED VENT HOLES (4 side faces only) -----
        // Skip front (0°, has laser/camera/LED) and back (180°, has USB-C)
        for (face_angle = [-120, -60, 60, 120]) {
            for (col = [0:vent_grid_cols-1]) {
                for (row = [0:vent_grid_rows-1]) {
                    rotate([0, 0, face_angle])
                    translate([
                        (col - (vent_grid_cols-1)/2) * vent_spacing,
                        hex_radius + 1,
                        vent_start_z + row * vent_spacing
                    ])
                    rotate([90, 0, 0])
                    cylinder(d = vent_hole_dia, h = wall_thickness + 15);
                }
            }
        }
    }

    // ----- MOUNTING POSTS w/ SHOCK ISOLATION -----
    floor_z = wall_thickness + dome_bulge;
    grommet_od = 9;       // silicone grommet outer diameter
    grommet_groove = 1.5; // groove depth for grommet seat

    // Galvo bracket (center, raised — galvos at laser height)
    // Posts have grommet grooves for M3 silicone washers
    for (x = [-galvo_width/2, galvo_width/2]) {
        for (y = [-galvo_depth/2, galvo_depth/2]) {
            translate([x, y + 10, floor_z])
            difference() {
                cylinder(d = grommet_od + 2, h = 10);
                cylinder(d = 2.5, h = 11);
                // Grommet seat groove at top of post
                translate([0, 0, 10 - grommet_groove])
                difference() {
                    cylinder(d = grommet_od, h = grommet_groove + 0.1);
                    cylinder(d = 2.5, h = grommet_groove + 0.2);
                }
            }
        }
    }

    // ESP32 (back-left, below galvos)
    for (x = [-esp32_length/2 + 5, esp32_length/2 - 5]) {
        translate([x - 15, -25, floor_z])
        difference() {
            cylinder(d = 8, h = 6);
            cylinder(d = 2.2, h = 7);
            // Grommet seat
            translate([0, 0, 6 - grommet_groove])
            difference() {
                cylinder(d = grommet_od, h = grommet_groove + 0.1);
                cylinder(d = 2.2, h = grommet_groove + 0.2);
            }
        }
    }

    // Driver boards (stacked vertically on right side)
    for (y = [-20, 20]) {
        translate([40, y, floor_z])
        difference() {
            cylinder(d = 8, h = 6);
            cylinder(d = 2.5, h = 7);
            // Grommet seat
            translate([0, 0, 6 - grommet_groove])
            difference() {
                cylinder(d = grommet_od, h = grommet_groove + 0.1);
                cylinder(d = 2.5, h = grommet_groove + 0.2);
            }
        }
    }

    // ===== SHOCK ABSORPTION: GALVO BAY BUMPER CHANNEL =====
    // Raised rail around galvo area — fill with neoprene foam strip
    // Protects galvos from lateral impacts (drop hits side of unit)
    galvo_bay_w = galvo_width + 20;
    galvo_bay_d = galvo_depth + 20;
    channel_w   = 5;     // foam strip width
    channel_h   = 15;    // wall height
    channel_t   = 1.5;   // wall thickness

    translate([0, 10, floor_z])
    difference() {
        // Outer rail
        linear_extrude(height = channel_h)
        offset(r = 3)
        square([galvo_bay_w + channel_w, galvo_bay_d + channel_w], center = true);

        // Inner cutout (galvo sits inside)
        translate([0, 0, -0.1])
        linear_extrude(height = channel_h + 1)
        offset(r = 2)
        square([galvo_bay_w - channel_t, galvo_bay_d - channel_t], center = true);

        // Outer trim (keeps it as a channel, not a solid block)
        translate([0, 0, -0.1])
        linear_extrude(height = channel_h + 1)
        offset(r = 4)
        square([galvo_bay_w + channel_w + channel_t*2, galvo_bay_d + channel_w + channel_t*2], center = true);
    }

    // ===== SHOCK ABSORPTION: LASER MODULE CRADLE =====
    // U-shaped cradle centered on laser aperture (x=0, toward front face)
    // Laser sits in foam-lined cradle, isolated from direct shell contact
    translate([-(laser_width + 10)/2, 30, floor_z])
    difference() {
        // Cradle block (centered on laser axis)
        cube([laser_width + 10, 16, laser_height/2]);
        // Inner pocket (laser drops in with foam wrap)
        translate([5, 2, 2])
        cube([laser_width, 12, laser_height/2 + 1]);
    }

    // ===== CORNER IMPACT BOSSES =====
    // Reinforced bumps at 6 hex corners (inside shell, on interior floor)
    // Absorb energy at most likely impact points on a drop
    for (i = [0:5]) {
        angle = i * 60 + 30;
        boss_r = hex_radius - wall_thickness - 18;  // pulled inward so they stay inside dome
        translate([boss_r * cos(angle), boss_r * sin(angle), floor_z])
        cylinder(d1 = 12, d2 = 8, h = 8);
    }
}

// ============================================================
// TOP HALF
// ============================================================
module top_half() {
    top_h = total_height - split_z;

    difference() {
        intersection() {
            enclosure_saucer();
            translate([0, 0, split_z + top_h/2])
            cube([hex_radius * 3, hex_radius * 3, top_h], center = true);
        }

        // Interior
        translate([0, 0, split_z - 0.1])
        hex_prism(hex_radius - wall_thickness, corner_radius,
                  edge_top - split_z + 0.1);

        // Lip recess
        translate([0, 0, split_z - 0.1])
        difference() {
            hex_prism(hex_radius - wall_thickness + lip_tolerance, corner_radius, lip_height + 0.1);
            hex_prism(hex_radius - wall_thickness - lip_inset - lip_tolerance, corner_radius, lip_height + 0.2);
        }

        // Screw holes
        for (i = [0:num_screws-1]) {
            angle = i * 360 / num_screws;
            translate([screw_post_r * cos(angle), screw_post_r * sin(angle), split_z])
            cylinder(d = insert_dia, h = top_h - dome_bulge);
        }

        // Top dome vent holes (PRIMARY exhaust — heat rises)
        // Larger grid than sides for maximum passive convection
        for (col = [-4:4]) {
            for (row = [-3:3]) {
                // Skip center 3x3 cluster to avoid screw holes
                if (!(abs(col) <= 1 && abs(row) <= 1))
                translate([col * vent_spacing, row * vent_spacing,
                          total_height - dome_bulge - wall_thickness])
                cylinder(d = vent_hole_dia, h = dome_bulge + wall_thickness + 1);
            }
        }

        // ----- PERFORATED VENT HOLES (4 side faces, above split) -----
        for (face_angle = [-120, -60, 60, 120]) {
            for (col = [0:vent_grid_cols-1]) {
                for (row = [0:vent_grid_rows-1]) {
                    rotate([0, 0, face_angle])
                    translate([
                        (col - (vent_grid_cols-1)/2) * vent_spacing,
                        hex_radius + 1,
                        vent_start_z + row * vent_spacing
                    ])
                    rotate([90, 0, 0])
                    cylinder(d = vent_hole_dia, h = wall_thickness + 15);
                }
            }
        }

        // Laser/camera clearance at split
        translate([0, hex_radius + 1, edge_bottom + edge_height/2])
        rotate([90, 0, 0])
        cylinder(d = laser_aperture + 2, h = wall_thickness + 10);

        translate([30, hex_radius + 1, edge_bottom + edge_height/2 - 2])
        rotate([90, 0, 0])
        cylinder(d = cam_lens_dia + 2, h = wall_thickness + 10);
    }
}

// ============================================================
// SILICONE SLEEVE (for visualization / mold reference)
// Big front opening (enclosure slides in/out)
// Back port holes: USB-C (rounded slot)
// Perforated panels on 4 side faces (aligned with enclosure for unobstructed airflow)
// Top dome vent grid (main exhaust — heat rises)
// ============================================================
module silicone_sleeve() {
    sleeve_r = hex_radius + sleeve_gap + sleeve_thickness;
    sleeve_cr = corner_radius + 2;
    sleeve_th = total_height + sleeve_thickness * 2;
    sleeve_eh = edge_height + sleeve_thickness;
    sleeve_db = (sleeve_th - sleeve_eh) / 2;

    // Hex apothem = perpendicular distance from center to flat face
    // This is the ACTUAL face surface distance (not vertex distance)
    sleeve_apothem = sleeve_r * cos(30);
    cut_len = 25;  // generous cut length — always punches through

    difference() {
        // Outer sleeve shape
        translate([0, 0, -sleeve_thickness])
        saucer_solid(sleeve_r, sleeve_cr, sleeve_th, sleeve_eh, sleeve_db);

        // Inner cutout (enclosure shape + gap)
        gap_r = hex_radius + sleeve_gap;
        saucer_solid(gap_r, corner_radius, total_height, edge_height, dome_bulge);

        // ----- FRONT OPENING (1 face + half of each adjacent face) -----
        // Enclosure slides in/out through here
        translate([0, hex_radius * 0.6, -sleeve_thickness - 1])
        linear_extrude(height = sleeve_th + 2)
        intersection() {
            circle(r = sleeve_r + 10);
            translate([0, sleeve_r * 0.35, 0])
            square([sleeve_r * 1.6, sleeve_r * 1.2], center = true);
        }

        // ----- BACK PORT HOLES (use apothem + generous cut_len) -----
        // USB-C
        translate([-20, -(sleeve_apothem + 2), total_height/2])
        rotate([-90, 0, 0])
        hull() {
            translate([-(usb_c_width/2 - usb_c_height/2), 0, 0])
            cylinder(d = usb_c_height + 5, h = cut_len);
            translate([(usb_c_width/2 - usb_c_height/2), 0, 0])
            cylinder(d = usb_c_height + 5, h = cut_len);
        }

        // (Fan exhaust hole removed — fan mounts internally)

        // ----- FINGER GRIP VENT OPENINGS (2 front-adjacent faces only) -----
        // Large openings next to laser/camera for pulling sleeve on/off.
        // Sized to fully clear the enclosure's perf grid underneath.
        for (face_angle = [-60, 60]) {
            rotate([0, 0, face_angle])
            translate([0, sleeve_apothem + 2, total_height / 2])
            rotate([90, 0, 0])
            hull() {
                translate([0, -12, 0]) cylinder(d = 36, h = cut_len);
                translate([0,  12, 0]) cylinder(d = 36, h = cut_len);
            }
        }

        // ----- PERFORATED VENT HOLES (2 back-adjacent faces) -----
        for (face_angle = [-120, 120]) {
            for (col = [0:vent_grid_cols-1]) {
                for (row = [0:vent_grid_rows-1]) {
                    rotate([0, 0, face_angle])
                    translate([
                        (col - (vent_grid_cols-1)/2) * vent_spacing,
                        sleeve_apothem + 2,
                        vent_start_z + row * vent_spacing
                    ])
                    rotate([90, 0, 0])
                    cylinder(d = vent_hole_dia + 1, h = cut_len);
                }
            }
        }

        // ----- TOP DOME VENT HOLES (main exhaust — heat rises) -----
        // Match enclosure grid, just slightly bigger for silicone
        for (col = [-4:4]) {
            for (row = [-3:3]) {
                if (!(abs(col) <= 1 && abs(row) <= 1))
                translate([col * vent_spacing, row * vent_spacing,
                          total_height - dome_bulge])
                cylinder(d = vent_hole_dia + 0.5, h = dome_bulge + sleeve_thickness + 2);
            }
        }

        // ----- TRIPOD HOLE (bottom center) -----
        translate([0, 0, -sleeve_thickness - 1])
        cylinder(d = tripod_insert_dia + 8, h = sleeve_thickness + 2);

        // ----- BRANDING (disabled for now — revisit later) -----
        // TODO: debossed text on dome slope — needs precise depth control

    }
}

// ============================================================
// RENDER
// ============================================================

// --- ASSEMBLED WITH SLEEVE (visualization) ---
color("SlateGray", 0.9) bottom_half();
color("SlateGray", 0.45) top_half();
color("DarkOliveGreen", 0.55) silicone_sleeve();

// --- ENCLOSURE ONLY (no sleeve) ---
// color("SlateGray", 0.9) bottom_half();
// color("SlateGray", 0.45) top_half();

// --- PRINT: Bottom half ---
// bottom_half();

// --- PRINT: Top half flipped ---
// translate([0, 0, total_height]) mirror([0, 0, 1]) top_half();

// --- SLEEVE MOLD OUTER (print this, pour silicone around enclosure) ---
// silicone_sleeve();
