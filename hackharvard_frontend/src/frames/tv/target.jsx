import {backend_url} from "../../backendUrl.jsx";
import "./target.css";

function Target(props) {
  const submitted = props.info.submitted_count || 0;
  const total = props.info.player_count || 0;

  return (
    <div id="target_screen">
      <div id="target_header">
        <div>Round {props.info.round_number}</div>
        <div>Recreate this image</div>
        <div>{submitted}/{total} prompts in</div>
      </div>
      {props.info.target_image && (
        <img id="target_image" src={backend_url + props.info.target_image} alt="Target" />
      )}
    </div>
  );
}

export default Target;
