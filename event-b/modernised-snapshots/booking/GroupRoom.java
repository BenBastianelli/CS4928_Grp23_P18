package booking;

import java.time.LocalDateTime;
import java.util.LinkedList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

public class GroupRoom implements Room {

    private final String name;
    private final String description;
    private final boolean hasWhiteboard;

    private final List<Booking> bookings = new LinkedList<>();

    protected GroupRoom(String name, String description, boolean hasWhiteboard) {
        this.name = name;
        this.description = description;
        this.hasWhiteboard = hasWhiteboard;
    }

    public String getName() {
        return this.name;
    }

    public String getDescription() {
        return this.description;
    }

    public boolean hasWhiteboard() {
        return this.hasWhiteboard;
    }

    public List<Booking> getBookings() {
        return List.copyOf(this.bookings);
    }

    private boolean available(Interval i) {
        for (Booking b : this.getBookings()) {
            if (b.getInterval().overlapsWith(i)) {
                return false;
            }
        }

        return true;
    }

    /*
    Due to the popularity of some specific group rooms,
     no user is allowed to have more than one upcoming booking for a group room.
    Also makes sure that the booking is valid and that the room is available.
     */
    public Optional<Booking> book(Interval i, User u) {
        if (this.userHasBookingAlready(u) || !this.available(i) || !startBeforeEnd(i)) {
            return Optional.empty();
        }

        Booking b = new Booking(i, u);
        bookings.add(b);

        return Optional.of(b);
    }

    private boolean userHasBookingAlready (User u) {
        for (Booking b : this.getBookings()) {
            if (b.getInterval().getEnd().isAfter(LocalDateTime.now()) && b.getBooker().equals(u)) {
                return true;
            }
        }

        return false;
    }

    private static boolean startBeforeEnd(Interval i) {
        return !(i.getEnd().isBefore(i.getStart()) || i.getStart().isBefore(LocalDateTime.now()));
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }

        if (o == null || this.getClass() != o.getClass()) {
            return false;
        }

        GroupRoom groupRoom = (GroupRoom) o;
        return Objects.equals(this.getName(), groupRoom.getName())
            && Objects.equals(this.hasWhiteboard(), groupRoom.hasWhiteboard());
    }

    @Override
    public int hashCode() {
        return Objects.hash(this.getName(), this.hasWhiteboard());
    }

    @Override
    public String toString() {
        return String.format(
                "Room %s \"%s\" #bookings: %s",
                this.getName(),
                this.getDescription(),
                this.getBookings().size()
        );
    }
}
