from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


menu_content = {
    "change_oil": "Change oil",
    "inflate_tires": "Inflate tires",
    "diagnostic": "Get diagnostic test"
}

class Menu(View):
    def get(self, request, *args, **kwargs):
        return render(request, "tickets/menu.html", {'menu': menu_content})




class NewTicket(View):
    line_of_cars = {"change_oil": [],
                "inflate_tires": [],
                "diagnostic": []}
    takes_minutes = {"change_oil": 2,
                "inflate_tires": 5,
                "diagnostic": 30}
    last_id = 0

    def count_waiting_time(self, service_name):
        change_oil_time = len(NewTicket.line_of_cars["change_oil"]) * NewTicket.takes_minutes["change_oil"]
        if service_name == "change_oil":
            return change_oil_time
        inflate_tires_time = change_oil_time\
                   + len(NewTicket.line_of_cars["inflate_tires"]) * NewTicket.takes_minutes["inflate_tires"]
        if service_name == "inflate_tires":
            return inflate_tires_time
        diagnostic_time = inflate_tires_time\
                          + len(NewTicket.line_of_cars["diagnostic"]) * NewTicket.takes_minutes["diagnostic"]
        if service_name == "diagnostic":
            return diagnostic_time

    def get(self, request, service_name, *args, **kwargs):
        NewTicket.last_id += 1
        minutes_to_wait = self.count_waiting_time(service_name)
        NewTicket.line_of_cars[service_name].append(NewTicket.last_id)
        return render(request, "tickets/ticket.html", {'ticket_number': NewTicket.last_id,
                                                       'minutes_to_wait': minutes_to_wait})


class Processing(View):
    last_ticket = 0
    def get(self, request, *args, **kwargs):
        return render(request, "tickets/processing.html",
                      {'change_oil_queue': len(NewTicket.line_of_cars["change_oil"]),
                       'inflate_tires_queue': len(NewTicket.line_of_cars["inflate_tires"]),
                       'get_diagnostic_queue': len(NewTicket.line_of_cars["diagnostic"])})

    def post(self, request, *args, **kwargs):
        if NewTicket.line_of_cars["change_oil"]:
            Processing.last_ticket = NewTicket.line_of_cars["change_oil"].pop(0)
            return HttpResponseRedirect('/next')
        if NewTicket.line_of_cars["inflate_tires"]:
            Processing.last_ticket = NewTicket.line_of_cars["inflate_tires"].pop(0)
            return HttpResponseRedirect('/next')
        if NewTicket.line_of_cars["diagnostic"]:
            Processing.last_ticket = NewTicket.line_of_cars["diagnostic"].pop(0)
            return HttpResponseRedirect('/next')
        Processing.last_ticket = 0
        return HttpResponseRedirect('/next')


class NextTicket(View):
    def get(self, request, *args, **kwargs):
        return render(request, "tickets/next_ticket.html", {'number_of_ticket': Processing.last_ticket})
