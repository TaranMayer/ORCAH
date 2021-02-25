"""
Names and permissions of Event Console user roles
"""
import eclib.apis as ecapis

team = "Team"
event_partner = "Event Partner"
referee = "Head Referee"
staff = "Staff"
observer = "Observer"
livestream = "Livestream"

RW_ = {
    team: (ecapis.chat, ecapis.inspection, ecapis.skills, ecapis.match_list,ecapis.rankings,ecapis.elims),
    event_partner: (ecapis.chat, ecapis.inspection_ctrl, ecapis.skills_ctrl, ecapis.meeting_ctrl, ecapis.event_ctrl, ecapis.tech_support, ecapis.match_list, ecapis.set_match,ecapis.rankings,ecapis.elims),
    referee: (ecapis.chat, ecapis.inspection_ctrl, ecapis.skills_ctrl, ecapis.match_list, ecapis.set_match,ecapis.rankings,ecapis.elims),
    staff: (ecapis.chat, ecapis.match_list,ecapis.rankings,ecapis.elims),
    observer: tuple(),
    livestream: tuple()
}

RO_ = {
    team: (ecapis.skills_scores,ecapis.stream),
    event_partner: (ecapis.skills_scores,ecapis.stream),
    referee: (ecapis.skills_scores,ecapis.stream),
    staff: (ecapis.inspection_ctrl, ecapis.skills_ctrl, ecapis.skills_scores,ecapis.stream),
    observer: (ecapis.chat, ecapis.inspection_ctrl, ecapis.skills_ctrl, ecapis.skills_scores,ecapis.stream),
    livestream: (ecapis.livestream,ecapis.stream)
}

STAFF_ROLES_ = (event_partner, referee, staff)
