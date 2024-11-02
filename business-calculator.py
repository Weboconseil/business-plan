import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def calculate_monthly_metrics(
    monthly_traffic,
    conversion_rate,
    average_basket,
    initial_capital,
    initial_stock,
    purchase_price_ratio,
    shipping_cost,
    marketing_budget
):
    # Calculs de base
    orders = monthly_traffic * (conversion_rate / 100)
    revenue = orders * average_basket
    
    # Coûts variables
    purchase_cost = revenue * (purchase_price_ratio / 100)
    shipping_total = orders * shipping_cost
    shopify_fees = (revenue * 0.029) + (orders * 0.30)
    
    # Coûts fixes
    fixed_costs = {
        'Shopify': 32,
        'SEO': 200,
        'Domain': 1.25,
        'Marketing': marketing_budget
    }
    total_fixed_costs = sum(fixed_costs.values())
    
    # Marges
    gross_margin = revenue - purchase_cost - shipping_total - shopify_fees
    net_margin = gross_margin - total_fixed_costs
    
    # Ratios
    gross_margin_rate = (gross_margin / revenue) * 100 if revenue > 0 else 0
    marketing_ratio = (marketing_budget / revenue) * 100 if revenue > 0 else 0
    break_even = total_fixed_costs / (gross_margin_rate / 100) if gross_margin_rate > 0 else 0
    
    return {
        'revenue': revenue,
        'orders': orders,
        'purchase_cost': purchase_cost,
        'shipping_total': shipping_total,
        'shopify_fees': shopify_fees,
        'fixed_costs': total_fixed_costs,
        'gross_margin': gross_margin,
        'net_margin': net_margin,
        'gross_margin_rate': gross_margin_rate,
        'marketing_ratio': marketing_ratio,
        'break_even': break_even
    }

def calculate_annual_projection(monthly_metrics):
    annual = {k: v * 12 for k, v in monthly_metrics.items()}
    annual['taxes'] = max(0, annual['net_margin'] * 0.20)
    annual['net_profit'] = annual['net_margin'] - annual['taxes']
    return annual

def main():
    st.title("Business Plan Financier")
    
    # Sidebar pour les hypothèses
    st.sidebar.header("Hypothèses de départ")
    
    monthly_traffic = st.sidebar.number_input(
        "Trafic mensuel initial",
        min_value=0,
        value=1000
    )
    
    conversion_rate = st.sidebar.number_input(
        "Taux de conversion (%)",
        min_value=0.0,
        max_value=100.0,
        value=2.0,
        step=0.1
    )
    
    average_basket = st.sidebar.number_input(
        "Panier moyen (€)",
        min_value=0.0,
        value=80.0
    )
    
    initial_capital = st.sidebar.number_input(
        "Capital initial (€)",
        min_value=0,
        value=10000
    )
    
    initial_stock = st.sidebar.number_input(
        "Stock initial (€)",
        min_value=0,
        value=3000
    )
    
    purchase_price_ratio = st.sidebar.number_input(
        "Prix d'achat (% du prix de vente)",
        min_value=0.0,
        max_value=100.0,
        value=40.0
    )
    
    shipping_cost = st.sidebar.number_input(
        "Frais de livraison par commande (€)",
        min_value=0.0,
        value=6.0
    )
    
    marketing_budget = st.sidebar.number_input(
        "Budget marketing mensuel (€)",
        min_value=0.0,
        value=300.0
    )
    
    # Calculs
    monthly = calculate_monthly_metrics(
        monthly_traffic,
        conversion_rate,
        average_basket,
        initial_capital,
        initial_stock,
        purchase_price_ratio,
        shipping_cost,
        marketing_budget
    )
    
    annual = calculate_annual_projection(monthly)
    
    # Affichage des résultats
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Résultats Mensuels")
        st.metric("Chiffre d'affaires", f"{monthly['revenue']:.2f}€")
        st.metric("Nombre de commandes", f"{monthly['orders']:.0f}")
        st.metric("Marge nette", f"{monthly['net_margin']:.2f}€")
    
    with col2:
        st.subheader("Ratios Clés")
        st.metric("Taux de marge brute", f"{monthly['gross_margin_rate']:.1f}%")
        st.metric("Ratio marketing", f"{monthly['marketing_ratio']:.1f}%")
        st.metric("Point mort mensuel", f"{monthly['break_even']:.2f}€")
    
    # Compte de résultat annuel
    st.header("Compte de Résultat Prévisionnel (Année 1)")
    
    results_df = pd.DataFrame([
        ["Chiffre d'affaires", annual['revenue']],
        ["Coût des marchandises", -annual['purchase_cost']],
        ["Frais de livraison", -annual['shipping_total']],
        ["Commissions Shopify", -annual['shopify_fees']],
        ["Charges fixes", -annual['fixed_costs']],
        ["Résultat d'exploitation", annual['net_margin']],
        ["Impôts (20%)", -annual['taxes']],
        ["Résultat net", annual['net_profit']]
    ], columns=["Poste", "Montant (€)"])
    
    st.dataframe(results_df.style.format({'Montant (€)': '{:.2f}'}))
    
    # Trésorerie
    st.header("Prévisions de Trésorerie")
    
    cash_m1 = initial_capital - initial_stock - monthly['fixed_costs'] - \
              monthly['purchase_cost'] - monthly['shipping_total'] - monthly['shopify_fees']
    
    annual_cash_in = initial_capital + annual['revenue']
    annual_cash_out = initial_stock + annual['fixed_costs'] + annual['purchase_cost'] + \
                     annual['shipping_total'] + annual['shopify_fees']
    final_balance = annual_cash_in - annual_cash_out
    
    cash_df = pd.DataFrame([
        ["Solde Mois 1", cash_m1],
        ["Entrées annuelles", annual_cash_in],
        ["Sorties annuelles", annual_cash_out],
        ["Solde fin d'année", final_balance]
    ], columns=["Poste", "Montant (€)"])
    
    st.dataframe(cash_df.style.format({'Montant (€)': '{:.2f}'}))
    
    # Graphique de rentabilité
    months = range(1, 13)
    cumulative_revenue = [monthly['revenue'] * m for m in months]
    cumulative_costs = [(monthly['fixed_costs'] + monthly['purchase_cost'] + 
                        monthly['shipping_total'] + monthly['shopify_fees']) * m for m in months]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=cumulative_revenue, name="Revenus cumulés"))
    fig.add_trace(go.Scatter(x=months, y=cumulative_costs, name="Coûts cumulés"))
    
    fig.update_layout(
        title="Projection de Rentabilité sur 12 mois",
        xaxis_title="Mois",
        yaxis_title="Euros (€)",
        showlegend=True
    )
    
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
