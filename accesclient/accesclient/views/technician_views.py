# technician_views.py
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
import json

from ..models import Repertoire
from ..forms import RepertoireForm


def get_technician_data(request, technician_id):
    try:
        technician = Repertoire.objects.get(pk=technician_id)
        data = {
            'type1': technician.type1,
            'media1': technician.media1,
            'type2': technician.type2,
            'media2': technician.media2,
            'type3': technician.type3,
            'media3': technician.media3,
            'type4': technician.type4,
            'media4': technician.media4,
        }
        return JsonResponse(data)
    except Repertoire.DoesNotExist:
        return JsonResponse({'error': 'Technician not found'}, status=404)


class ManageTechniciansView(View):
    def get(self, request):
        technicians = Repertoire.objects.filter(client=request.user.username)
        form = RepertoireForm()
        return render(request, 'Astreinte/manage_technicians.html', {
            'technicians': technicians,
            'form': form
        })

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        action = data.get('action')

        if action == 'edit':
            return self.edit_technician(request, data)
        elif action == 'delete':
            return self.delete_technician(request, data)
        elif action == 'add':
            return self.create_technician(request, data)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

    def edit_technician(self, request, data):
        repertoire_id = data.get('id_repertoire')
        try:
            repertoire = Repertoire.objects.get(
                id_repertoire=repertoire_id,
                client=request.user.username
            )
            form = RepertoireForm(data, instance=repertoire)

            if form.is_valid():
                form.save()
                return JsonResponse({'success': True, 'message': 'Technician updated successfully'})
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        except Repertoire.DoesNotExist:
            return JsonResponse({'error': 'Technician not found'}, status=404)

    def delete_technician(self, request, data):
        repertoire_id = data.get('id_repertoire')
        try:
            repertoire = Repertoire.objects.get(
                id_repertoire=repertoire_id,
                client=request.user.username
            )
            repertoire.delete()
            return JsonResponse({'success': True, 'message': 'Technician deleted successfully'})
        except Repertoire.DoesNotExist:
            return JsonResponse({'error': 'Technician not found'}, status=404)

    def create_technician(self, request, data):
        form = RepertoireForm(data)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.client = request.user.username
            new_entry.save()
            return JsonResponse({
                'success': True,
                'message': 'Technician added successfully',
                'technician': {
                    'id_repertoire': new_entry.id_repertoire,
                    'client': new_entry.client,
                    'nom_technicien': new_entry.nom_technicien,
                    'type1': new_entry.type1,
                    'media1': new_entry.media1,
                    'type2': new_entry.type2,
                    'media2': new_entry.media2,
                }
            })
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
