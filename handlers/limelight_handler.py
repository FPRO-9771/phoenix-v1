import math
import limelight
import limelightresults


class LimelightHandler:
    def __init__(self, debug=True):
        self.discovered_limelights = limelight.discover_limelights(debug=debug)
        self.limelight_instance = None

        if self.discovered_limelights:
            print(f"##### Limelight init: Limelight found and active:", self.discovered_limelights)
            limelight_address = self.discovered_limelights[0]
            self.limelight_instance = limelight.Limelight(limelight_address)
            self.limelight_instance.pipeline_switch(0)  # Switch to AprilTag detection pipeline
            self.limelight_instance.enable_websocket()
        else:
            print(f"##### Limelight init: ERROR: No Limelights found")

    def read_results(self):
        """Get the raw limelight results"""
        print(f"##### Limelight read_results: starting")
        if self.limelight_instance:
            print(f"##### Limelight read_results: there is an instance")
            result = self.limelight_instance.get_latest_results()
            print("Limelight read_results: result:", result)
            parsed_result = limelightresults.parse_results(result)

            if parsed_result is not None:
                print(
                    f"##### Limelight valid targets: ", parsed_result.validity, ", pipelineIndex: ", parsed_result.pipeline_id,
                    ", Targeting Latency: ", parsed_result.targeting_latency
                )
                for tag in parsed_result.fiducialResults:
                    print(
                        f"##### Limelight  read_results: AprilTag ID: {tag.fiducial_id}, Robot Pose: {tag.robot_pose_target_space}")

                return parsed_result
        return None

    def get_target_data(self, target_tag_id=None):

        parsed_result = self.read_results()

        if not (parsed_result and parsed_result.validity and len(parsed_result.fiducialResults) > 0):
            print("##### Limelight get_target_data: No valid targets found")
            return None

        print(f"##### Limelight get_target_data: Found {len(parsed_result.fiducialResults)} valid targets")

        selected_fiducial = None

        # If a specific tag ID is requested
        if target_tag_id is not None:
            print(f"##### Limelight get_target_data: Looking for tag ID {target_tag_id}")
            # Look for the requested tag ID in the results
            for fiducial in parsed_result.fiducialResults:
                if fiducial.fiducial_id == target_tag_id:
                    selected_fiducial = fiducial
                    print(f"##### Limelight get_target_data: Found requested tag ID: {target_tag_id}")
                    break

        # If no specific tag was requested or the requested tag wasn't found
        if selected_fiducial is None:
            # Find the closest tag
            closest_distance = float('inf')
            for fiducial in parsed_result.fiducialResults:
                # Calculate distance to this tag
                tx_pos = fiducial.transform_camera.x
                ty_pos = fiducial.transform_camera.y
                tz_pos = fiducial.transform_camera.z
                distance = math.sqrt(tx_pos ** 2 + ty_pos ** 2 + tz_pos ** 2)

                if distance < closest_distance:
                    closest_distance = distance
                    selected_fiducial = fiducial

            if selected_fiducial:
                print(
                    f"##### Limelight get_target_data: Using closest tag (ID: {selected_fiducial.fiducial_id}, distance: {closest_distance:.2f}m)")

        # If we still don't have a selected fiducial (shouldn't happen if we had valid results)
        if selected_fiducial is None:
            print("##### Limelight get_target_data: No valid fiducial found")
            return None

        # Process the selected fiducial into a clean data object
        tx_pos = selected_fiducial.transform_camera.x
        ty_pos = selected_fiducial.transform_camera.y
        tz_pos = selected_fiducial.transform_camera.z
        distance = math.sqrt(tx_pos ** 2 + ty_pos ** 2 + tz_pos ** 2)

        # Pitch (up/down tilt)
        # Yaw (left/right rotation)
        # Roll (twist) of the tag

        target_data = {
            'tag_id': selected_fiducial.fiducial_id,
            'tx': selected_fiducial.target_x_degrees,
            'ty': selected_fiducial.target_y_degrees,
            'area': selected_fiducial.target_area,
            'pitch': selected_fiducial.pitch,
            'yaw': selected_fiducial.yaw,
            'roll': selected_fiducial.roll,
            'x_pos': tx_pos,
            'y_pos': ty_pos,
            'z_pos': tz_pos,
            'distance': distance,
            'robot_pose': selected_fiducial.robot_pose_target_space if hasattr(selected_fiducial,
                                                                               'robot_pose_target_space') else None
        }

        return target_data

    def cleanup(self):
        if self.limelight_instance:
            self.limelight_instance.disable_websocket()