import datetime
from datetime import timedelta
import math
#Django modules
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q
from django.db import connection
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.cache import cache_page
#Project models
from esports.models import League_Game, League_Team, Match, Match_Survey,Org_League

# Render login page
def login(request):
    return render(request, 'esports/login.html')

# Render the home page with league overview and recent matches
def index(request):
    # If user is a site manage show admin dashboard button
    is_admin = request.user.groups.filter(name='#####').exists()
    subdomain = request.META.get('HTTP_HOST').split('.')[0]  # Get subdomain from request
    schema = connection.get_schema()
    if subdomain == 'public' or subdomain == '127': # For testing
        subdomain = 'gse' # Default schema
    org = Org_League.objects.get(org_schema=subdomain)  # Get organization data
  
    context = {
        'is_admin':is_admin,
        'schema':schema,
        'org':org,
    }
    return render(request, 'esports/index.html', context)


# Render public-facing match ticker (allows embedding in iframes)
@xframe_options_exempt # Allows view to be displayed in iframe - for use on other websites
def ticker(request):
    # Get league games and recent match data
    active_league_games, last_week_matches, img_path = get_recent_match_data()
    
    context = {
        'active_league_games':active_league_games,
        'last_week_matches':last_week_matches,
        'img_path':img_path,
    }
    return render(request, 'esports/ticker.html',context)


# Retrieve active league games and recent matches
def get_recent_match_data():
    # Get all active matches for currently active league games
    active_matches = Match.objects.filter(match_date__league_game__activate=True)

     # Get all currently active league games, ordered by start date
    active_league_games = League_Game.objects.filter(activate=True).order_by('start_date')

    # Define date range for "recent" matches (past 7 days + today)
    now = datetime.datetime.now(datetime.timezone.utc)
    startdate = now - timedelta(days=7)
    enddate = now + timedelta(days=1)

    # Filter matches to only include those in the recent range
    last_week_matches = active_matches.filter(match_date__match_date__range=[startdate.date(), enddate.date()])

    # Exclude matches missing valid teams or marked as a bye week
    last_week_matches = last_week_matches.exclude(home_team__school_team=None)
    last_week_matches = last_week_matches.exclude(away_team__school_team=None)
    last_week_matches = last_week_matches.exclude(~Q(away_team__bye_week_name="None"))
    last_week_matches = last_week_matches.exclude(~Q(home_team__bye_week_name="None"))

    # Static image/media path for rendering thumbnails or icons
    img_path = 'media'

    return active_league_games, last_week_matches, img_path


# Custom 404 error handler
def handler404(request, exception):
    context = {}
    response = render(request, "errors/404.html", context=context)
    response.status_code = 404
    return response


# Custom 500 error handler
def handler500(request):
    context = {}
    response = render(request, "errors/500.html", context=context)
    response.status_code = 500
    return response


# View for showing upcoming competitions (cached for 5 seconds)
@cache_page(5)
def competitions(request):
    # If user is a site manage show admin dashboard button
    is_admin = request.user.groups.filter(name='Site Manager').exists()

    # Find all active games for displaying teams and standings
    active_matches = Match.objects.filter(match_date__league_game__activate = True)
    active_league_games = League_Game.objects.filter(activate = True).order_by('start_date')
    contenders_games = active_league_games.filter(league_level__level_of_play="Contenders")
    active_league_games = active_league_games.filter(league_level__level_of_play="Champion")

    # Get date range for upcoming matches
    now = datetime.datetime.now(datetime.timezone.utc)
    enddate = now + timedelta(days=6)

    # Filter upcoming week matches
    upcoming_week_matches = active_matches.filter(match_date__match_date__range=[now.date(),enddate.date()])
    upcoming_week_matches = upcoming_week_matches.exclude(home_team__school_team=None)
    upcoming_week_matches = upcoming_week_matches.exclude(away_team__school_team=None)
    upcoming_week_matches = upcoming_week_matches.exclude(~Q(away_team__bye_week_name="None"))
    upcoming_week_matches = upcoming_week_matches.exclude(~Q(home_team__bye_week_name="None"))
    
    img_path = 'media'

    # If tournament brackets are active, load and show brackets
    active_tourneys = active_league_games.filter(show_bracket=True)
    num_active = len(active_tourneys)

    context = {
        'is_admin':is_admin,
        'active_league_games':active_league_games,
        'contenders_games':contenders_games,
        'upcoming_week_matches':upcoming_week_matches,
        'img_path':img_path,
        'num_active':num_active,
    }
    return render(request, 'esports/competitions.html', context)


# Render privacy policy page
def privacy_policy(request):
    # If user is a site manage show admin dashboard button
    is_admin = request.user.groups.filter(name='Site Manager').exists()

    # Get subdomain from request
    subdomain = request.META.get('HTTP_HOST').split('.')[0]
    schema = connection.get_schema()
    if subdomain == 'public' or subdomain == '127' or subdomain == '' or subdomain == 'tenant': # For testing
        subdomain = 'gse'
    org = Org_League.objects.get(org_schema=subdomain)
    img_path = 'media'

    context = {
        'is_admin':is_admin,
        'img_path':img_path,
        'schema':schema,
        'org':org,
    }
    return render(request, 'esports/privacy_policy.html', context)


# Send a welcome email to a coach
def send_email(request, coach_email):
    subdomain = request.META.get('HTTP_HOST').split('.')[0]
    if subdomain == 'public':
        subdomain = 'gse'
    org = Org_League.objects.get(org_schema=subdomain)
    subject = 'Join ' + org.org_schema.upper() + ' Portal'
    message = 'Welcome to the '  + org.org_schema.upper() +' Family!\n\nYour email address, '+coach_email +', has been approved for GSE Portal account creation! The GSE Portal is your go-to hub for all GSE competition resources, including season registration, team and roster management, and access to season schedules.\n\nGet Started in 3 Easy Steps:\n\nLog In: Visit https://'+ org.org_schema +'.esportsforedu.com/login/ using your approved email address through Google or Microsoft Single Sign-On.\n\nAdd Your Discord ID: You\'ll be prompted to provide your Discord ID. Please have this information ready, as it\'s a required step to proceed. If you haven\'t joined the GSE Discord, you\'ll want to do that before creating your account. Reach out to chris@gsepsorts.org if you haven\'t been invited to the GSE Discord.\n\nWatch the Demo: We\'ve put together a short demonstration video of the GSE Portal to help you get started. Check it out here!\nhttps://drive.google.com/file/d/16crA15OUVPpQS_5OINE9DKc_SezzM8bJ/view?usp=sharing\n\nNeed Help Finding Your Discord User ID?\n\nA Discord user ID is an 18- or 19-digit number that differs from your username. Follow these steps to find it:\n\nOpen the Discord app or website. Click the Settings icon in the lower-left corner. Go to Advanced options and enable Developer Mode. Exit Settings, click your username, and then click it again to copy your Discord user ID. You can now paste your ID number into the GSE portal when creating your account.\n\nIf you need any help reach out to jim@gsesports.org or regina@gsesports.org and they\'ll help you get your account created! '
    from_email = org.org_email
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, [coach_email])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
    else:
        return HttpResponse('Make sure all fields are entered and valid.')


# Calculate point total from match results
def calculate_points(wins,losses,ties,forfeits):
    return wins*3+ties


# Update match and team records after score submission
def submit_scores(match, home_report, away_report):
     # Copy match report data to match object
    match.home_score = home_report.team_score
    match.away_score = home_report.other_score
    match.home_forfeit = home_report.team_forfeit
    match.away_forfeit = home_report.other_forfeit
    match.home_awaysportsmanship = home_report.team_othersportsmanship
    match.away_homesportsmanship = away_report.team_othersportsmanship
    match.home_awayontime = home_report.team_otherontime
    match.away_homeontime = away_report.team_otherontime
    match.home_pog = home_report.team_pog
    match.home_away_pog = home_report.other_pog
    match.away_pog = away_report.team_pog
    match.away_home_pog = away_report.other_pog
    match.home_roster_correct = True if away_report.roster_correct == "Yes" or match.match_date.league_game.league_level.level_of_play != "Champion" else False
    match.away_roster_correct = True if home_report.roster_correct == "Yes" or match.match_date.league_game.league_level.level_of_play != "Champion" else False
    match.home_scouting_correct = True if away_report.scouting_correct == "Yes" or match.match_date.league_game.scouting_required == False else False
    match.away_scouting_correct = True if home_report.scouting_correct == "Yes" or match.match_date.league_game.scouting_required == False else False
    match.home_roster = home_report.team_roster
    match.away_roster = away_report.team_roster
    if match.home_forfeit and match.away_forfeit:
        match.away_score = 0
        match.home_score = 0
    elif match.away_forfeit:
        if match.home_team.league_game.series_length < 3:
            match.home_score = match.home_team.league_game.series_length
        else:
            match.home_score = math.floor(match.home_team.league_game.series_length/2) + 1
    elif match.home_forfeit:
        if match.away_team.league_game.series_length < 3:
            match.away_score = match.away_team.league_game.series_length
        else:
            match.away_score = math.floor(match.home_team.league_game.series_length/2) + 1

    # Save match as complete and update team records
    match.complete = True
    match.save()

    # Update win/loss/tie/forfeit stats
    home_team = match.home_team
    away_team = match.away_team
    if match.home_forfeit and match.away_forfeit:
        home_team.forfeits = home_team.forfeits + 1
        away_team.forfeits = away_team.forfeits + 1
        home_team.losses = home_team.losses + 1
        away_team.losses = away_team.losses + 1
    elif match.home_forfeit:
        home_team.forfeits = home_team.forfeits + 1
        away_team.wins = away_team.wins + 1
        home_team.losses = home_team.losses + 1
    elif match.away_forfeit:
        away_team.forfeits = away_team.forfeits + 1
        home_team.wins = home_team.wins + 1
        away_team.losses = away_team.losses + 1
    elif int(match.home_score) > int(match.away_score):
        home_team.wins = home_team.wins + 1
        away_team.losses = away_team.losses + 1
    elif int(match.home_score) < int(match.away_score):
        home_team.losses = home_team.losses + 1
        away_team.wins = away_team.wins + 1
    elif int(match.home_score) == int(match.away_score):
        home_team.ties = home_team.ties + 1
        away_team.ties = away_team.ties + 1
    home_team.score_for = home_team.score_for + int(match.home_score)
    home_team.score_against = home_team.score_against + int(match.away_score)
    away_team.score_for = away_team.score_for + int(match.away_score)
    away_team.score_against = away_team.score_against + int(match.home_score)
    
    # Save new point totals
    home_team.points = calculate_points(home_team.wins,home_team.losses,home_team.ties,home_team.forfeits)
    away_team.points = calculate_points(away_team.wins,away_team.losses,away_team.ties,away_team.forfeits)
    home_team.save()
    away_team.save()

    # Delete the reports after use
    home_report.delete()
    away_report.delete()

    # Handle tournament bracket progression
    bracket = match.bracket_number
    tourney_matches = Match.objects.filter(match_date__league_game=home_team.league_game)
    tourney_matches = tourney_matches.filter(tourney_match=True)
    tourney_matches = tourney_matches.filter(bracket_number=bracket)
    if len(tourney_matches) > 0:
        league_teams = League_Team.objects.filter(league_game=home_team.league_game)
        tourney_teams = league_teams.filter(tournament_team=True)
        tourney_teams = tourney_teams.filter(bracket_number=home_team.bracket_number)
        team_count=len(tourney_teams)
        round1_count = team_count/2
        tourn_num = math.ceil(match.tourney_number/2)
        next_match_num = int(round1_count + tourn_num)
        if next_match_num <= team_count - 1:
            next_match = tourney_matches.get(tourney_number=next_match_num)
            if match.tourney_number%2==1:
                if match.home_score > match.away_score:
                    next_match.home_team=home_team
                else:
                    next_match.home_team=away_team
            else:
                if match.home_score > match.away_score:
                    next_match.away_team=home_team
                else:
                    next_match.away_team=away_team
            next_match.save()
            if next_match.home_team != None and next_match.away_team != None:
                if next_match.home_team.seeding > next_match.away_team.seeding:
                    temp = next_match.home_team
                    next_match.home_team = next_match.away_team
                    next_match.away_team = temp
                    next_match.save()
                home_survey = Match_Survey(match=next_match, team = next_match.home_team, other_team = next_match.away_team, team_score = 0, other_score=0,team_forfeit=False,other_forfeit=False,team_pog=None,other_pog=None,complete=False,tourney_survey=True)
                away_survey = Match_Survey(match=next_match, team = next_match.away_team, other_team = next_match.home_team, team_score = 0, other_score=0,team_forfeit=False,other_forfeit=False,team_pog=None,other_pog=None,complete=False,tourney_survey=True)
                home_survey.save()
                away_survey.save()
