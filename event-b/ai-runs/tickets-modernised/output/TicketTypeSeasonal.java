package tickets;

import java.util.EnumSet;
import java.util.Objects;
import java.util.Set;

public class TicketTypeSeasonal implements TicketType {

    private final String name;
    private final double price;
    private final Set<Zone> validZones;
    private final Season validSeason;

    public TicketTypeSeasonal(
        String name,
        double price,
        Set<Zone> validZones,
        Season validSeason
    ) {
        this.name = name;
        this.price = price;
        this.validZones = EnumSet.copyOf(validZones);
        this.validSeason = validSeason;
    }

    /*
    Make sure that the trip is during the correct season.
    Also checks that the ticket is valid in the zones of the trip.
     */
    @Override
    public boolean isValidFor(Trip t, User u) {
        return this.getValidZones().contains(t.getStartZone())
            && this.getValidZones().contains(t.getEndZone())
            && this.getValidSeason().isDateWithin(t.getTripStartTime());
    }

    public String getName() {
        return this.name;
    }

    public double getPrice() {
        return this.price;
    }

    public Set<Zone> getValidZones() {
        return EnumSet.copyOf(this.validZones);
    }
    
    public Season getValidSeason() {
        return this.validSeason;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }

        if (o == null || this.getClass() != o.getClass()) {
            return false;
        }

        TicketTypeSeasonal ticketType = (TicketTypeSeasonal) o;
        return Objects.equals(this.getName(), ticketType.getName())
            && Objects.equals(this.getValidSeason(), ticketType.getValidSeason())
            && Objects.equals(this.getValidZones(), ticketType.getValidZones())
            && Objects.equals(this.getPrice(), ticketType.getPrice());
    }

    @Override
    public int hashCode() {
        return Objects.hash(this.getName(), this.getPrice(), this.getValidSeason());
    }

    @Override
    public String toString() {
        return String.format("Ticket %s ", this.getName());
    }
}
