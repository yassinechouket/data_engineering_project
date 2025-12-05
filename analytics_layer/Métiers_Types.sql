CREATE VIEW v_pollution_24h AS
SELECT 
    a.nom_arrondissement,
    AVG(m.valeur_mesuree) AS pollution_moyenne,
    MAX(m.valeur_mesuree) AS pollution_max,
    COUNT(m.id_mesure) AS nombre_mesures
FROM arrondissement a
JOIN capteur c ON a.id_arrondissement = c.id_arrondissement
JOIN mesure m ON c.id_capteur = m.id_capteur
WHERE m.date_heure_mesure >= NOW() - INTERVAL '24 HOURS'
  AND c.type_capteur IN ('pollution', 'qualité air', 'air')
GROUP BY a.nom_arrondissement
ORDER BY pollution_moyenne DESC;




CREATE VIEW taux_de_disponibilité AS
SELECT 
    a.nom_arrondissement,
    COUNT(c.id_capteur) AS total_capteurs,
    SUM(CASE WHEN c.statut = 'actif' THEN 1 ELSE 0 END) AS capteurs_actifs,
    ROUND(
        CASE 
            WHEN COUNT(c.id_capteur) = 0 THEN 0
            ELSE (SUM(CASE WHEN c.statut = 'actif' THEN 1 ELSE 0 END)::DECIMAL / COUNT(c.id_capteur)) * 100
        END, 2
    ) AS taux_disponibilite_pourcentage
FROM arrondissement a
LEFT JOIN capteur c ON a.id_arrondissement = c.id_arrondissement
GROUP BY a.nom_arrondissement
ORDER BY taux_disponibilite_pourcentage DESC;

    
CREATE VIEW trajets_véhicules_autonomes AS
SELECT 
    t.plaque_immatriculation,
    v.type_vehicule,
    v.energie_utilisee,
    t.origine,
    t.destination,
    t.date_heure_depart,
    t.duree_minutes,
    t.economie_co2_kg
FROM trajet t
JOIN vehicule_autonome v ON t.plaque_immatriculation = v.plaque_immatriculation
ORDER BY t.economie_co2_kg DESC;


CREATE VIEW interventions_predictives AS
SELECT 
    COUNT(DISTINCT i.id_intervention) AS nombre_interventions_predictives,
    SUM(i.impact_environnemental_co2_kg) AS economie_co2_totale_kg,
    SUM(i.cout_euros) AS cout_total_euros,
    AVG(i.duree_minutes) AS duree_moyenne_minutes
FROM intervention i
WHERE i.nature_intervention = 'predictive'
  AND i.date_heure_intervention >= DATE_TRUNC('month', CURRENT_DATE)
  AND i.date_heure_intervention < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month';




CREATE VIEW citoyens_plus_engages AS
SELECT 
    c.id_citoyen,
    c.nom_citoyen,
    c.prenom_citoyen,
    c.email,
    c.score_engagement_ecologique,
    COUNT(p.id_consultation) AS nombre_participations,
    SUM(CASE WHEN p.vote = 'pour' THEN 1 ELSE 0 END) AS votes_pour,
    c.preferences_mobilite
FROM citoyen c
LEFT JOIN participation_citoyenne p ON c.id_citoyen = p.id_citoyen
GROUP BY c.id_citoyen, c.nom_citoyen, c.prenom_citoyen, c.email, 
         c.score_engagement_ecologique, c.preferences_mobilite
ORDER BY c.score_engagement_ecologique DESC, nombre_participations DESC;
