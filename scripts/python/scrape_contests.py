from draft_kings import Client
from draft_kings import Sport
import pandas as pd
import datetime


def obj_to_list(obj):
    return list(vars(obj).values())


def get_contests_df(clt, sport):
    print("Getting Contests")
    contests = clt.contests(sport=sport)
    cutoff = (
        pd.Timestamp.utcnow().normalize()
        + pd.Timedelta(1, "day")
        + pd.Timedelta(10, "hours")
    )

    # Contest Details
    lst = list(map(lambda contest: obj_to_list(contest), contests.contests))
    if len(lst):
        cols = list(vars(contests.contests[0]).keys())
        ct_df = pd.DataFrame(lst, columns=cols)
        entry_cols = ["entry_fee", "entry_max", "entry_total"]
        entry_df = pd.DataFrame(
            ct_df.entries_details.apply(obj_to_list).to_list(), columns=entry_cols
        )
        ct_df = pd.concat([ct_df, entry_df], axis=1)
        ct_df.drop("entries_details", axis=1, inplace=True)
        ct_df.sport = ct_df.sport.apply(lambda enum: enum.value)
        ct_df = ct_df[ct_df.starts_at <= cutoff]
        ct_df.starts_at = ct_df.starts_at.astype(str)
        ct_df.drop(["entry_total"], axis=1, inplace=True)
        ct_df.set_index("contest_id", drop=True, inplace=True)
        ct_df.sort_index(inplace=True)
        if not len(ct_df):
            ct_df = None
    else:
        ct_df = None

    # Draft Group Details
    lst = list(map(lambda contest: obj_to_list(contest), contests.draft_groups))
    if len(lst):
        cols = list(vars(contests.draft_groups[0]).keys())
        dg_df = pd.DataFrame(lst, columns=cols)
        dg_df.sport = dg_df.sport.apply(lambda enum: enum.value)
        dg_df = dg_df[dg_df.starts_at <= cutoff]
        dg_df.starts_at = dg_df.starts_at.astype(str)
        dg_df.set_index("draft_group_id", drop=True, inplace=True)
        dg_df.sort_index(inplace=True)
        if not len(dg_df):
            dg_df = None
    else:
        dg_df = None

    return ct_df, dg_df


def get_draftables(clt, draft_group_ids):
    competitions = {}
    players = {}
    print("Getting draftables")
    for id in draft_group_ids:
        draftables = clt.draftables(draft_group_id=id)
        for competition in draftables.competitions:
            competitions[competition.competition_id] = competition
        players[id] = draftables.players

    # Competition Details
    temp = list(competitions.values())
    lst = list(map(lambda contest: obj_to_list(contest), temp))
    if len(lst):
        cols = list(vars(temp[0]).keys())
        comp_df = pd.DataFrame(lst, columns=cols)
        comp_df.away_team = comp_df.away_team.apply(lambda team: team.abbreviation)
        comp_df.home_team = comp_df.home_team.apply(lambda team: team.abbreviation)
        comp_df.sport = comp_df.sport.apply(lambda enum: enum.value)
        comp_df.starts_at = comp_df.starts_at.astype(str)
        comp_df.drop(["state_description", "weather"], axis=1, inplace=True)
        comp_df.set_index("competition_id", drop=True, inplace=True)
        comp_df.sort_index(inplace=True)
    else:
        comp_df = None

    # Draft Group Game Details
    print("Getting draft group details")
    games_list = []
    for id in draft_group_ids:
        deets = clt.draft_group_details(id)
        game_ids = list(map(lambda game: game.game_id, deets.games))
        games_list.append([id, game_ids])
    game_df = (
        pd.DataFrame(games_list, columns=["draft_group_id", "game_id"])
        .explode("game_id")
        .reset_index(drop=True)
    )
    game_df.sort_values(["draft_group_id", "game_id"], inplace=True)

    # Player Details
    players_lst = []
    for id in draft_group_ids:
        temp = players[id]
        lst = list(map(lambda contest: obj_to_list(contest), temp))
        if len(temp):
            cols = list(vars(temp[0]).keys())
            player_df = pd.DataFrame(lst, columns=cols)
            player_df.loc[:, "draft_group_id"] = id
            players_lst.append(player_df)

    if len(players_lst):
        players_df = pd.concat(players_lst)
        players_df.loc[:, "competition_id"] = players_df.competition_details.apply(
            lambda comp: comp.competition_id
        )
        players_df.loc[:, "name"] = players_df.name_details.apply(
            lambda name: name.display
        )
        players_df.loc[:, "team"] = players_df.team_details.apply(
            lambda team: team.abbreviation
        )
        players_df.drop(
            [
                "competition_details",
                "name_details",
                "image_details",
                "draft_alerts",
                "news_status_description",
                "team_details",
            ],
            axis=1,
            inplace=True,
        )
        players_df.set_index("draftable_id", drop=True, inplace=True)
        players_df.sort_index(inplace=True)
        col_order = [
            "draft_group_id",
            "player_id",
            "roster_slot_id",
            "competition_id",
            "name",
            "team",
            "position_name",
            "salary",
            "is_disabled",
            "is_swappable",
        ]
        players_df = players_df[col_order]
    else:
        players_df = None

    return comp_df, game_df, players_df


def get_contest_info(clt, contest_type_ids):
    contest_type_list = []
    lineup_templates = {}

    # Contest Type Details
    print("Getting Contest Type Details")
    for contest_type_id in contest_type_ids:
        game_type = clt.game_type_rules(contest_type_id)
        lst = obj_to_list(game_type)
        lst += obj_to_list(lst[-1])
        del lst[7]
        lineup_templates[contest_type_id] = lst[5]
        del lst[5]
        contest_type_list.append(lst)

    cols = list(vars(game_type).keys())
    del cols[7]
    del cols[5]
    cols += ["has_salary_cap", "salary_max", "salary_min"]
    contest_df = pd.DataFrame(contest_type_list, columns=cols).set_index("game_type_id")
    contest_df.sort_index(inplace=True)

    # Lineup Construction Details
    lineups_lst = []
    for contest_type_id, lineup_template in lineup_templates.items():
        slots = list(
            map(lambda slot: slot.roster_slot_details.roster_slot_id, lineup_template)
        )
        lineup_df = pd.DataFrame(
            pd.value_counts(slots).items(), columns=["roster_slot_id", "count"]
        )
        lineup_df.loc[:, "contest_type_id"] = contest_type_id
        lineups_lst.append(lineup_df)
    lineups_df = pd.concat(lineups_lst)
    lineups_df = lineups_df[["contest_type_id", "roster_slot_id", "count"]].reset_index(
        drop=True
    )
    lineups_df.sort_values(["contest_type_id", "roster_slot_id"], inplace=True)

    return contest_df, lineups_df


if __name__ == "__main__":
    clt = Client()
    today = datetime.datetime.today().strftime("%m-%d-%Y")

    ct_df, dg_df = get_contests_df(clt, Sport.NBA)

    if ct_df is not None:
        ct_df.to_csv(f"data/contests/{today}.csv")
        print("Successfully wrote contests to files")
    elif dg_df is None:
        print("No contests today")
        exit(2)

    if dg_df is not None:
        contest_type_ids = dg_df.contest_type_id.unique()
        draft_group_ids = dg_df.index.values

        comp_df, game_df, player_df = get_draftables(clt, draft_group_ids)
        contest_df, lineups_df = get_contest_info(clt, contest_type_ids)

        dg_df.to_csv(f"data/draft-groups/{today}.csv")
        game_df.to_csv(f"data/draft-group-games/{today}.csv", index=False)
        contest_df.to_csv(f"data/contest-types/{today}.csv")
        lineups_df.to_csv(f"data/lineup-requirements/{today}.csv", index=False)
        print(
            "Successfully wrote draft groups, draft group games, contest types,"
            + " and lineup reqs to files"
        )

        if comp_df is not None:
            comp_df.to_csv(f"data/competitions/{today}.csv")
        if player_df is not None:
            player_df.to_csv(f"data/draftables/{today}.csv")

        print("Draft Group Details successfully written to files")
    else:
        print("No draft groups found")

    exit(0)
