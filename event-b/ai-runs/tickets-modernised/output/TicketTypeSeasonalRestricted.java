package tickets;

import java.util.EnumSet;
import java.util.Objects;
import java.util.Set;

public class TicketTypeSeasonalRestricted implements TicketType {

    private final String name;
    private final double price;
    private final Set<Zone> validZones;
    private final Season validSeason;
    private final Set<User.Occupation> validOccupations;

    public TicketTypeSeasonalRestricted(
        String name,
        double price,
        Set<Zone> validZones,
        Season validSeason,
        Set<User.Occupation> validOccupations
    ) {
        this.name = name;
        this.price = price;
        this.validZones = EnumSet.copyOf(validZones);
        this.validSeason = validSeason;
        this.validOccupations = EnumSet.noneOf(User.Occupation.class);
        this.validOccupations.addAll(validOccupations);
    }

    @Override
    public boolean isValidFor(Trip t, User u) {
        return this.getValidZones().contains(t.getStartZone())
            && this.getValidZones().contains(t.getEndZone())
            && this.getValidSeason().isDateWithin(t.getTripStartTime())
            && this.getValidOccupations().contains(u.getOccupation());
    }

    @Override
    public String getName() {
        return this.name;
    }

    @Override
    public double getPrice() {
        return this.price;
    }

    @Override
    public Set<Zone> getValidZones() {
        return EnumSet.copyOf(this.validZones);
    }

    public Season getValidSeason() {
        return this.validSeason;
    }

    public Set<User.Occupation> getValidOccupations() {
        Set<User.Occupation> occupations =
            EnumSet.noneOf(User.Occupation.class);
        occupations.addAll(this.validOccupations);
        return occupations;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }

        if (o == null || this.getClass() != o.getClass()) {
            return false;
        }

        TicketTypeSeasonalRestricted ticketType =
            (TicketTypeSeasonalRestricted) o;

        return Objects.equals(this.getName(), ticketType.getName())
            && Objects.equals(this.getPrice(), ticketType.getPrice())
            && Objects.equals(this.getValidZones(), ticketType.getValidZones())
            && Objects.equals(
                this.getValidSeason(),
                ticketType.getValidSeason()
            )
            && Objects.equals(
                this.getValidOccupations(),
                ticketType.getValidOccupations()
            );
    }

    @Override
    public int hashCode() {
        return Objects.hash(
            this.getName(),
            this.getPrice(),
            this.getValidZones(),
            this.getValidSeason(),
            this.getValidOccupations()
        );
    }

    @Override
    public String toString() {
        return String.format("Ticket %s ", this.getName());
    }
}