from django.shortcuts import render,redirect

def accueil(request):
    return render(request, 'accueil.html') 

def connexion(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        # Ici, tu ajouteras plus tard la vérification réelle avec la base de données MySQL
        
        # Redirection vers les interfaces spécifiques
        if role == 'client':
            return redirect('interface_client') # Interface 3
        elif role == 'serveur':
            return redirect('interface_serveur') # Interface 4
        elif role == 'chef_cuisinier':
            return redirect('interface_chef') # Interface 5
        elif role == 'cuisinier':
            return redirect('interface_cuisinier') # Interface 6
        elif role == 'gestionnaire_stock':
            return redirect('interface_stock') # Interface 7
        elif role == 'livreur':
            return redirect('interface_livreur') # Interface 8
        elif role == 'admin':
            return redirect('interface_admin') # Interface 9
            
    return render(request, 'connexion.html')

# Simulation des autres vues pour tes tests
def interface_client(request): return render(request, 'client.html')
def interface_serveur(request): return render(request, 'serveur.html')
def interface_chef(request): return render(request, 'chef.html')
def interface_cuisinier(request): return render(request, 'cuisinier.html')
def interface_stock(request): return render(request, 'stock.html')
def interface_livreur(request): return render(request, 'livreur.html')
def interface_admin(request): return render(request, 'admin.html')