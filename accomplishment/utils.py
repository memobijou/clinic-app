from accomplishment.models import Accomplishment


def get_accomplishment_scores(instance: Accomplishment):
    users = instance.users.all()
    subject_areas = instance.subject_areas.all()

    subject_area_users = users.filter(profile__subject_area__in=subject_areas)

    current_score_percentage = instance.get_current_score_percentage(subject_area_users)

    user_accomplishments = instance.user_accomplishments.select_related("accomplishment")
    subject_area_users_scores = instance.get_subject_area_users_scores(subject_area_users, user_accomplishments)
    non_subject_area_users_scores = instance.get_non_subject_area_users_scores(subject_area_users, user_accomplishments)

    return {"current_score": current_score_percentage, "subject_area_users_scores": subject_area_users_scores,
            "non_subject_area_users_scores": non_subject_area_users_scores}
