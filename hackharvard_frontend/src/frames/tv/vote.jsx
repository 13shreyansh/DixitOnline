import { useState } from "react"
import {backend_url} from "../../backendUrl.jsx";
import "./vote.css"

function TvVote(props) {

    let items = []
    for (let card in props.images) {
        const item = props.images[card];
        const image = item.image || item;
        items.push(
            <div key={image} className="match_card">
              <div className="match_card_number">{Number(card) + 1}</div>
              <img src={backend_url + image} alt={"Match candidate"}/>
            </div>);
    }

    return (
        <div id="container">
            <div id="match_vote">
              <div id="match_target_panel">
                <div className="match_label">Target</div>
                <img src={backend_url + props.target_image} alt="Target" />
              </div>
              <div id="match_candidates">
                {items}
                <div id="anonymous_note">Images are anonymous until the reveal.</div>
              </div>
            </div>
        </div>
    )
}

export default TvVote
