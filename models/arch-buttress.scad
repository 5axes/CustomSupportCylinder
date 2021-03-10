//----------------------------------------------
// Arch buttress Support Style
// Size must be 1mm height 
//----------------------------------------------
$fn=40;

translate([-0.5,-0.5,-1.0]) 
union() {
    translate([0.5,0.55,0.0]) rotate([90, 0, 0]) {
			linear_extrude(height=0.1) {
				polygon(points=[[-0.62,0],[-1.19,0],[-1,0.4],[-0.1,1],[0.01,1],[0.01,0.95],[-0.35,0.5]], convexity=1);
			}
		}
    translate([-0.4,0.5,0.0]) cylinder ( h = 0.02, r = 0.3, center = false);
}
