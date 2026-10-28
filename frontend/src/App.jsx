import React, { useState, useEffect } from "react";
import {
  MapPin,
  TicketPercent,
  Star,
  Calendar,
  Clock, 
  Users,
  CheckCircle2,
  Search,
  Sparkles,
  X,
  ChevronRight,
  Navigation,
  Utensils,
} from "lucide-react";

const API_BASE_URL = "http://localhost:8000";

// Fallback local caso o backend FastAPI ainda não esteja rodando no momento do teste visual
const RESTAURANTES_MOCK = [
  {
    id: 1,
    nome: "Haus Bier & Gastronomia Alemã",
    categoria: "Alemão",
    endereco: "Av. Cônsul Carlos Renaux, 412",
    bairro: "Centro I",
    latitude: -27.0978,
    longitude: -48.9168,
    cupom_destaque: "20% OFF no jantar até 19h30",
    desconto_percentual: 20,
    avaliacao: 4.9,
    imagem_url:
      "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80",
    total_mesas: 4,
    posMapa: { top: "44%", left: "48%" },
  },
  {
    id: 2,
    nome: "Trattoria Nonna Fenarreco",
    categoria: "Italiano",
    endereco: "Rua Hercílio Luz, 210",
    bairro: "São Luiz",
    latitude: -27.1025,
    longitude: -48.921,
    cupom_destaque: "15% OFF + Sobremesa Grátis",
    desconto_percentual: 15,
    avaliacao: 4.8,
    imagem_url:
      "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80",
    total_mesas: 3,
    posMapa: { top: "68%", left: "28%" },
  },
  {
    id: 3,
    nome: "Brusque Burger & Craft Beer",
    categoria: "Hamburgueria",
    endereco: "Av. Beira Rio, 890",
    bairro: "Santa Rita",
    latitude: -27.0942,
    longitude: -48.9125,
    cupom_destaque: "25% OFF terças e quartas",
    desconto_percentual: 25,
    avaliacao: 4.7,
    imagem_url:
      "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=800&q=80",
    total_mesas: 3,
    posMapa: { top: "26%", left: "66%" },
  },
  {
    id: 4,
    nome: "Kori Sushi Lounge",
    categoria: "Japonês",
    endereco: "Rua Moritz Germano Hoffmann, 105",
    bairro: "Centro II",
    latitude: -27.0995,
    longitude: -48.9102,
    cupom_destaque: "10% OFF no Rodízio Premium",
    desconto_percentual: 10,
    avaliacao: 4.9,
    imagem_url:
      "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=800&q=80",
    total_mesas: 3,
    posMapa: { top: "56%", left: "74%" },
  },
];

const HORARIOS_DISPONIVEIS = [
  { hora: "18:30", ocioso: true, bonus: "Horário VIP (+Desconto Garantido)" },
  { hora: "19:00", ocioso: true, bonus: "Horário VIP (+Desconto Garantido)" },
  { hora: "19:30", ocioso: true, bonus: "Último horário com cupom máximo" },
  { hora: "20:00", ocioso: false, bonus: "Alta procura" },
  { hora: "20:30", ocioso: false, bonus: "Alta procura" },
  { hora: "21:00", ocioso: false, bonus: "Horário normal" },
];

export default function App() {
  const [restaurantes, setRestaurantes] = useState(RESTAURANTES_MOCK);
  const [categoriaAtiva, setCategoriaAtiva] = useState("Todos");
  const [busca, setBusca] = useState("");
  const [restauranteFocadoMapa, setRestauranteFocadoMapa] = useState(null);
  const [usandoApiReal, setUsandoApiReal] = useState(false);

  // Estados do Modal de Reserva
  const [restauranteSelecionado, setRestauranteSelecionado] = useState(null);
  const [dataReserva, setDataReserva] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [horarioReserva, setHorarioReserva] = useState("19:00");
  const [qtdPessoas, setQtdPessoas] = useState(2);
  const [nomeUsuario, setNomeUsuario] = useState("");
  const [emailUsuario, setEmailUsuario] = useState("");
  const [telefoneUsuario, setTelefoneUsuario] = useState("");
  const [carregandoReserva, setCarregandoReserva] = useState(false);
  const [erroReserva, setErroReserva] = useState(null);
  const [reservaConfirmada, setReservaConfirmada] = useState(null);
  const [minhasReservas, setMinhasReservas] = useState([]);

  // Tenta carregar da API FastAPI; se estiver offline, mantém o mock interativo
  useEffect(() => {
    async function carregarRestaurantes() {
      try {
        const res = await fetch(`${API_BASE_URL}/restaurantes`);
        if (!res.ok) throw new Error("API offline");
        const dados = await res.json();
        // Mapeia posições visuais no mapa para os itens vindos do banco
        const posicoes = [
          { top: "44%", left: "48%" },
          { top: "68%", left: "28%" },
          { top: "26%", left: "66%" },
          { top: "56%", left: "74%" },
        ];
        const enriquecidos = dados.map((item, idx) => ({
          ...item,
          posMapa: posicoes[idx % posicoes.length],
        }));
        setRestaurantes(enriquecidos);
        setUsandoApiReal(true);
      } catch {
        setUsandoApiReal(false);
      }
    }
    carregarRestaurantes();
  }, []);

  const categorias = ["Todos", "Alemão", "Italiano", "Hamburgueria", "Japonês"];

  const restaurantesFiltrados = restaurantes.filter((r) => {
    const matchCategoria =
      categoriaAtiva === "Todos" || r.categoria === categoriaAtiva;
    const matchBusca =
      r.nome.toLowerCase().includes(busca.toLowerCase()) ||
      r.bairro.toLowerCase().includes(busca.toLowerCase()) ||
      r.categoria.toLowerCase().includes(busca.toLowerCase());
    return matchCategoria && matchBusca;
  });

  const abrirFluxoReserva = (restaurante) => {
    setRestauranteSelecionado(restaurante);
    setReservaConfirmada(null);
    setErroReserva(null);
  };

  const fecharModal = () => {
    setRestauranteSelecionado(null);
    setReservaConfirmada(null);
    setErroReserva(null);
  };

  const confirmarReserva = async (e) => {
    e.preventDefault();
    setCarregandoReserva(true);
    setErroReserva(null);

    const payload = {
      restaurante_id: restauranteSelecionado.id,
      data_reserva: dataReserva,
      horario_reserva: `${horarioReserva}:00`,
      qtd_pessoas: Number(qtdPessoas),
      nome_usuario: nomeUsuario,
      email_usuario: emailUsuario,
      telefone_usuario: telefoneUsuario,
    };

    try {
      if (usandoApiReal) {
        const response = await fetch(`${API_BASE_URL}/reservas`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "Erro ao realizar reserva.");
        }

        const confirmacao = await response.json();
        setReservaConfirmada(confirmacao);
        setMinhasReservas((prev) => [confirmacao, ...prev]);
      } else {
        // Simulação caso o usuário esteja testando apenas o frontend
        await new Promise((r) => setTimeout(r, 700));
        const confirmacaoSimulada = {
          id: Math.floor(Math.random() * 1000),
          codigo_confirmacao: `BRQ-${Math.random()
            .toString(36)
            .substring(2, 8)
            .toUpperCase()}`,
          restaurante_nome: restauranteSelecionado.nome,
          mesa_identificador:
            qtdPessoas <= 2
              ? "Mesa 01 (2 Lugares)"
              : qtdPessoas <= 4
              ? "Mesa 02 (4 Lugares)"
              : "Mesa 03 (Grupo)",
          data_reserva: dataReserva,
          horario_reserva: horarioReserva,
          qtd_pessoas: qtdPessoas,
          cupom_aplicado: restauranteSelecionado.cupom_destaque,
          status: "CONFIRMADA",
        };
        setReservaConfirmada(confirmacaoSimulada);
        setMinhasReservas((prev) => [confirmacaoSimulada, ...prev]);
      }
    } catch (err) {
      setErroReserva(err.message);
    } finally {
      setCarregandoReserva(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex justify-center">
      {/* Container Mobile-First (estilo App Nativo em telas maiores) */}
      <div className="w-full max-w-md bg-white min-h-screen shadow-2xl flex flex-col relative pb-16">
        {/* HEADER */}
        <header className="bg-gradient-to-r from-orange-600 to-rose-600 text-white p-4 rounded-b-3xl shadow-md">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="flex items-center gap-1.5 text-orange-100 text-xs font-medium">
                <MapPin className="w-3.5 h-3.5" />
                <span>Brusque, Santa Catarina</span>
              </div>
              <h1 className="text-xl font-extrabold tracking-tight flex items-center gap-1.5">
                <Utensils className="w-5 h-5" />
                MesaBrusque
              </h1>
            </div>
            <span
              className={`text-[11px] px-2.5 py-1 rounded-full font-semibold ${
                usandoApiReal
                  ? "bg-emerald-500/20 text-emerald-100 border border-emerald-300/30"
                  : "bg-white/20 text-white"
              }`}
            >
              {usandoApiReal ? "API Conectada" : "Modo Demo"}
            </span>
          </div>

          {/* Barra de Busca */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              placeholder="Buscar restaurante, bairro ou culinária..."
              className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-white text-slate-800 text-sm placeholder-slate-400 focus:outline-none shadow-inner"
            />
          </div>
        </header>

        {/* MAPA INTERATIVO DE BRUSQUE (Simulação Visual c/ Pinos de Desconto) */}
        <section className="px-4 mt-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
              <Navigation className="w-3.5 h-3.5 text-orange-600" />
              Mapa de Mesas & Descontos Hoje
            </h2>
            <span className="text-xs text-orange-600 font-semibold">
              Toque em um pino
            </span>
          </div>

          <div className="relative h-48 w-full rounded-2xl overflow-hidden border border-slate-200 shadow-sm bg-[#e8eef2]">
            {/* Malha urbana estilizada de Brusque + Rio Itajaí-Mirim */}
            <svg
              className="w-full h-full object-cover opacity-80"
              viewBox="0 0 400 200"
              fill="none"
            >
              <rect width="400" height="200" fill="#eef2f6" />
              {/* Áreas verdes / Parques */}
              <circle cx="80" cy="40" r="35" fill="#d8f3dc" />
              <circle cx="330" cy="150" r="45" fill="#d8f3dc" />
              {/* Quadras e avenidas */}
              <path
                d="M0 50 H400 M0 110 H400 M0 160 H400 M90 0 V200 M200 0 V200 M310 0 V200"
                stroke="#ffffff"
                strokeWidth="6"
              />
              {/* Rio Itajaí-Mirim cortando Brusque + Av. Beira Rio */}
              <path
                d="M -10 140 Q 120 70, 230 95 T 410 45"
                stroke="#90e0ef"
                strokeWidth="16"
                 strokeLinecap="round"
              />
              <path
                d="M -10 128 Q 120 58, 230 83 T 410 33"
                stroke="#ffd166"
                strokeWidth="3"
                strokeDasharray="4 4"
              />
            </svg>

            {/* Rótulos de Bairros de Brusque */}
            <span className="absolute top-2 left-3 text-[10px] font-bold text-slate-400 uppercase">
              São Luiz
            </span>
            <span className="absolute top-3 right-3 text-[10px] font-bold text-slate-400 uppercase">
              Santa Rita
            </span>
            <span className="absolute bottom-2 left-1/3 text-[10px] font-bold text-slate-500 uppercase">
              Centro • Rio Itajaí-Mirim
            </span>

            {/* Pinos dos Restaurantes no Mapa */}
            {restaurantesFiltrados.map((rest) => {
              const selecionado = restauranteFocadoMapa?.id === rest.id;
              return (
                <button
                  key={rest.id}
                  onClick={() => setRestauranteFocadoMapa(rest)}
                  style={{
                    top: rest.posMapa?.top || "50%",
                    left: rest.posMapa?.left || "50%",
                  }}
                  className={`absolute -translate-x-1/2 -translate-y-1/2 transition-all duration-200 ${
                    selecionado ? "z-30 scale-110" : "z-10 hover:scale-105"
                  }`}
                >
                  <div
                    className={`flex items-center gap-1 px-2.5 py-1 rounded-full font-bold text-xs shadow-lg border ${
                      selecionado
                        ? "bg-slate-900 text-white border-white"
                        : "bg-orange-600 text-white border-white"
                    }`}
                  >
                    <TicketPercent className="w-3.5 h-3.5" />
                    <span>-{rest.desconto_percentual}%</span>
                  </div>
                </button>
              );
            })}

            {/* Mini-card flutuante quando clica num pino do mapa */}
            {restauranteFocadoMapa && (
              <div className="absolute bottom-2 left-2 right-2 bg-white/95 backdrop-blur-sm p-2.5 rounded-xl shadow-lg border border-slate-100 flex items-center justify-between z-40">
                <div className="flex items-center gap-2.5">
                  <img
                    src={restauranteFocadoMapa.imagem_url}
                    alt={restauranteFocadoMapa.nome}
                    className="w-11 h-11 rounded-lg object-cover"
                  />
                  <div>
                    <p className="text-xs font-bold text-slate-800 leading-tight">
                      {restauranteFocadoMapa.nome}
                    </p>
                    <p className="text-[11px] text-emerald-600 font-semibold">
                      {restauranteFocadoMapa.cupom_destaque}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => abrirFluxoReserva(restauranteFocadoMapa)}
                    className="bg-orange-600 text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow"
                  >
                    Reservar
                  </button>
                  <button
                    onClick={() => setRestauranteFocadoMapa(null)}
                    className="p-1 text-slate-400 hover:text-slate-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* FILTRO DE CATEGORIAS */}
        <section className="px-4 mt-4">
          <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
            {categorias.map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoriaAtiva(cat)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition ${
                  categoriaAtiva === cat
                    ? "bg-slate-900 text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </section>

        {/* MINHAS RESERVAS ATIVAS (SE HOUVER) */}
        {minhasReservas.length > 0 && (
          <section className="px-4 mt-4">
            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-3">
              <p className="text-xs font-bold text-emerald-800 flex items-center gap-1.5 mb-1">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Sua Última Reserva Confirmada
              </p>
              <div className="flex items-center justify-between text-xs text-emerald-900">
                <div>
                  <span className="font-semibold">
                    {minhasReservas[0].restaurante_nome}
                  </span>{" "}
                  • {minhasReservas[0].horario_reserva.slice(0, 5)} (
                  {minhasReservas[0].qtd_pessoas}p)
                </div>
                <span className="font-mono font-bold bg-emerald-200/70 px-2 py-0.5 rounded text-emerald-950">
                  {minhasReservas[0].codigo_confirmacao}
                </span>
              </div>
            </div>
          </section>
        )}

        {/* LISTAGEM DE RESTAURANTES & CUPONS */}
        <section className="px-4 mt-4 flex-1 space-y-3.5">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-extrabold text-slate-800">
              Restaurantes com Benefícios Hoje
            </h2>
            <span className="text-xs text-slate-400">
              {restaurantesFiltrados.length} locais
            </span>
          </div>

          {restaurantesFiltrados.map((rest) => (
            <div
              key={rest.id}
              className="bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition overflow-hidden"
            >
              <div className="relative h-36 w-full">
                <img
                  src={rest.imagem_url}
                  alt={rest.nome}
                  className="w-full h-full object-cover"
                />
                {/* Badge do Cupom para Horário Ocioso */}
                {rest.cupom_destaque && (
                  <div className="absolute top-3 left-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{rest.cupom_destaque}</span>
                  </div>
                )}
                {/* Nota de Avaliação */}
                <div className="absolute bottom-2.5 right-3 bg-slate-900/80 backdrop-blur-sm text-white text-xs font-bold px-2.5 py-1 rounded-lg flex items-center gap-1">
                  <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                  <span>{rest.avaliacao.toFixed(1)}</span>
                </div>
              </div>

              <div className="p-3.5">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-orange-600">
                      {rest.categoria} • {rest.bairro}
                    </span>
                    <h3 className="text-base font-extrabold text-slate-900 leading-snug">
                      {rest.nome}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {rest.endereco}
                    </p>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <div className="text-xs text-slate-600">
                    <span className="font-bold text-emerald-600">
                      {rest.total_mesas} mesas
                    </span>{" "}
                    cadastradas hoje
                  </div>

                  <button
                    onClick={() => abrirFluxoReserva(rest)}
                    className="bg-orange-600 hover:bg-orange-700 active:scale-95 transition text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-1 shadow-sm shadow-orange-600/20"
                  >
                    <span>Reservar c/ Cupom</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </section>

        {/* MODAL DO FLUXO DE RESERVA */}
        {restauranteSelecionado && (
          <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4">
            <div className="bg-white w-full max-w-md rounded-t-3xl sm:rounded-3xl p-5 shadow-2xl max-h-[92vh] overflow-y-auto animate-in slide-in-from-bottom">
              {/* Cabeçalho do Modal */}
              <div className="flex items-start justify-between border-b border-slate-100 pb-3">
                <div>
                  <span className="text-xs font-bold text-orange-600 uppercase">
                    Reserva Instantânea
                  </span>
                  <h3 className="text-lg font-extrabold text-slate-900">
                    {restauranteSelecionado.nome}
                  </h3>
                  <p className="text-xs text-slate-500">
                    {restauranteSelecionado.endereco} —{" "}
                    {restauranteSelecionado.bairro}
                  </p>
                </div>
                <button
                  onClick={fecharModal}
                  className="p-1.5 rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* TELA 1: FORMULÁRIO DE RESERVA */}
              {!reservaConfirmada ? (
                <form onSubmit={confirmarReserva} className="space-y-4 mt-4">
                  {/* Banner do Cupom Ativo */}
                  {restauranteSelecionado.cupom_destaque && (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-3 flex items-center gap-2.5">
                      <TicketPercent className="w-6 h-6 text-emerald-600 shrink-0" />
                      <div>
                        <p className="text-xs font-bold text-emerald-900">
                          Benefício incluído gratuitamente:
                        </p>
                        <p className="text-xs font-semibold text-emerald-700">
                          {restauranteSelecionado.cupom_destaque}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Data e Quantidade de Pessoas */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1 flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5 text-orange-600" />
                        Data
                      </label>
                      <input
                        type="date"
                        required
                        value={dataReserva}
                        onChange={(e) => setDataReserva(e.target.value)}
                        className="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:border-orange-500"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1 flex items-center gap-1">
                        <Users className="w-3.5 h-3.5 text-orange-600" />
                        Pessoas na Mesa
                      </label>
                      <select
                        value={qtdPessoas}
                        onChange={(e) => setQtdPessoas(Number(e.target.value))}
                        className="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:border-orange-500 bg-white"
                      >
                        {[1, 2, 3, 4, 5, 6, 8].map((num) => (
                          <option key={num} value={num}>
                            {num} {num === 1 ? "pessoa" : "pessoas"}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Seleção de Horário (Destacando Horários Ociosos) */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-orange-600" />
                      Escolha o Horário
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {HORARIOS_DISPONIVEIS.map((item) => {
                        const ativo = horarioReserva === item.hora;
                        return (
                          <button
                            type="button"
                            key={item.hora}
                            onClick={() => setHorarioReserva(item.hora)}
                            className={`p-2 rounded-xl border text-center transition relative ${
                              ativo
                                ? "bg-orange-600 text-white border-orange-600 shadow-sm"
                                : "bg-white text-slate-700 border-slate-200 hover:border-orange-300"
                            }`}
                          >
                            <div className="text-xs font-extrabold">
                              {item.hora}
                            </div>
                            {item.ocioso && (
                              <div
                                className={`text-[10px] font-bold ${
                                  ativo ? "text-orange-100" : "text-emerald-600"
                                }`}
                              >
                                -{restauranteSelecionado.desconto_percentual}% OFF
                              </div>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Dados do Cliente */}
                  <div className="space-y-2.5 pt-2 border-t border-slate-100">
                    <p className="text-xs font-bold text-slate-700">
                      Seus dados para gerar o voucher
                    </p>
                    <input
                      type="text"
                      required
                      placeholder="Seu nome completo"
                      value={nomeUsuario}
                      onChange={(e) => setNomeUsuario(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs focus:outline-none focus:border-orange-500"
                    />
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="email"
                        required
                        placeholder="seu@email.com"
                        value={emailUsuario}
                        onChange={(e) => setEmailUsuario(e.target.value)}
                        className="w-full border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs focus:outline-none focus:border-orange-500"
                      />
                      <input
                        type="tel"
                        required
                        placeholder="(47) 99999-0000"
                        value={telefoneUsuario}
                        onChange={(e) => setTelefoneUsuario(e.target.value)}
                        className="w-full border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs focus:outline-none focus:border-orange-500"
                      />
                    </div>
                  </div>

                  {erroReserva && (
                    <div className="bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold p-3 rounded-xl">
                      {erroReserva}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={carregandoReserva}
                    className="w-full bg-gradient-to-r from-orange-600 to-rose-600 text-white font-extrabold text-sm py-3 rounded-2xl shadow-lg shadow-orange-600/25 hover:opacity-95 disabled:opacity-50"
                  >
                    {carregandoReserva
                      ? "Verificando mesas disponíveis..."
                      : "Confirmar Reserva e Garantir Cupom"}
                  </button>
                </form>
              ) : (
                /* TELA 2: VOUCHER DE CONFIRMAÇÃO */
                <div className="mt-5 text-center space-y-4">
                  <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>

                  <div>
                    <h4 className="text-lg font-extrabold text-slate-900">
                      Mesa Reservada com Sucesso!
                    </h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Apresente o código abaixo na recepção do restaurante.
                    </p>
                  </div>

                  {/* Voucher Card */}
                  <div className="bg-slate-50 border-2 border-dashed border-slate-300 rounded-2xl p-4 text-left space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-[11px] font-bold text-slate-400 uppercase">
                        Código do Voucher
                      </span>
                      <span className="text-sm font-mono font-extrabold bg-slate-900 text-white px-2.5 py-1 rounded-lg">
                        {reservaConfirmada.codigo_confirmacao}
                      </span>
                    </div>

                    <div className="text-xs text-slate-700 space-y-1 pt-2 border-t border-slate-200">
                      <p>
                        <strong>Restaurante:</strong>{" "}
                        {reservaConfirmada.restaurante_nome}
                      </p>
                      <p>
                        <strong>Mesa Alocada:</strong>{" "}
                        {reservaConfirmada.mesa_identificador}
                      </p>
                      <p>
                        <strong>Data e Hora:</strong>{" "}
                        {reservaConfirmada.data_reserva} às{" "}
                        {reservaConfirmada.horario_reserva.slice(0, 5)}
                      </p>
                      <p>
                        <strong>Pessoas:</strong>{" "}
                        {reservaConfirmada.qtd_pessoas} lugares
                      </p>
                      {reservaConfirmada.cupom_aplicado && (
                        <p className="text-emerald-700 font-bold pt-1">
                          🎁 Cupom ativo: {reservaConfirmada.cupom_aplicado}
                        </p>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={fecharModal}
                    className="w-full bg-slate-900 text-white font-bold text-xs py-3 rounded-xl"
                  >
                    Voltar para o Mapa de Brusque
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

