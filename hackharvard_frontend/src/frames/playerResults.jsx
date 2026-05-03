import 'src/App.css'
import "./playerResults.css"

// player_display_results
// {
//    is_active_player: bool
//    result: "everybody"|"split"|"nobody",
//    guessed_active_player: bool,
//    num_bonus_votes: int
//    player_round_score : int,
//    Player_total_score: int
// }


function PlayerResults(props) {
    const result_banner = props.info.message || "Round complete";

    return (
        <div id="player_results_container">
            <div id="pr_game_result">
                {result_banner}
            </div>
            <div id="pr_round_score">
                round score: <strong>{props.info.player_round_score}</strong>
            </div>
            <div id="pr_total_score">
                total score: <strong>{props.info.player_total_score}</strong>
            </div>
        </div>
    )
}

export default PlayerResults
