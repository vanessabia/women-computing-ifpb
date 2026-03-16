import matplotlib.pyplot as plt

# valores do gráfico
valores = [3480, 2350, 1750, 1130, 850, 550]

# nomes anonimizados
campus = [
    "Campus A",
    "Campus B",
    "Campus C",
    "Campus D",
    "Campus E",
    "Campus F"
]

plt.figure(figsize=(10,6))
plt.bar(campus, valores)

plt.title("Matrículas por campus")
plt.ylabel("Quantidade de matrículas")

plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("matriculas_campus_anonimizado.png", dpi=300)
plt.show()